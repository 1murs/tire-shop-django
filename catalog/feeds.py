"""XML feeds for price aggregators like E-Katalog, Hotline, etc."""
from django.http import StreamingHttpResponse
from django.utils import timezone
from .models import Tire, Disk, Supplier


def generate_ekatalog_xml(request):
    """Generate XML feed for E-Katalog - streaming version for large datasets"""

    # Get filter parameters
    supplier_ids = request.GET.getlist('supplier')
    if not supplier_ids:
        suppliers_param = request.GET.get('suppliers', '')
        if suppliers_param:
            supplier_ids = [s.strip() for s in suppliers_param.split(',') if s.strip()]

    product_type = request.GET.get('type', 'all')
    in_stock_param = request.GET.get('in_stock')  # 1=в наявності, 0=під замовлення, без параметра=всі

    base_url = request.build_absolute_uri('/').rstrip('/')

    def generate():
        now = timezone.now().strftime('%Y-%m-%d %H:%M')

        # Header
        yield '<?xml version="1.0" encoding="UTF-8"?>\n'
        yield f'<yml_catalog date="{now}">\n'
        yield '<shop>\n'
        yield '<name>КМ/Ч 120</name>\n'
        yield '<company>КМ/Ч 120</company>\n'
        yield f'<url>{base_url}</url>\n'
        yield '<currencies>\n<currency id="UAH" rate="1"/>\n</currencies>\n'
        yield '<categories>\n'
        yield '<category id="1">Шини</category>\n'
        yield '<category id="2">Диски</category>\n'
        yield '</categories>\n'
        yield '<offers>\n'

        # Tires
        if product_type in ['all', 'tires']:
            tires = Tire.objects.select_related('brand').only(
                'id', 'slug', 'price', 'in_stock', 'image',
                'brand__name', 'model_name', 'width', 'profile', 'diameter',
                'season', 'load_index', 'speed_index'
            )

            if supplier_ids:
                tires = tires.filter(supplier_id__in=supplier_ids)
            if in_stock_param == '1':
                tires = tires.filter(in_stock=True)
            elif in_stock_param == '0':
                tires = tires.filter(in_stock=False)

            season_map = {'summer': 'Літня', 'winter': 'Зимова', 'all_season': 'Всесезонна'}

            for tire in tires.iterator(chunk_size=1000):
                available = "true"
                name = f"{tire.brand.name} {tire.model_name} {tire.width}/{tire.profile} R{tire.diameter}"
                season = season_map.get(tire.season, '')

                yield f'<offer id="tire_{tire.id}" available="{available}">\n'
                yield f'<url>{base_url}/tires/{tire.slug}/</url>\n'
                yield f'<price>{int(tire.price)}</price>\n'
                yield '<currencyId>UAH</currencyId>\n'
                yield '<categoryId>1</categoryId>\n'
                if tire.image:
                    yield f'<picture>{base_url}/media/{tire.image}</picture>\n'
                yield f'<name>{escape_xml(name)}</name>\n'
                yield f'<vendor>{escape_xml(tire.brand.name)}</vendor>\n'
                desc = f"Шина {name}. Сезон: {season}."
                if tire.load_index:
                    desc += f" Індекс навантаження: {tire.load_index}."
                if tire.speed_index:
                    desc += f" Індекс швидкості: {tire.speed_index}."
                yield f'<description>{escape_xml(desc)}</description>\n'
                yield f'<param name="Ширина">{tire.width}</param>\n'
                yield f'<param name="Профіль">{tire.profile}</param>\n'
                yield f'<param name="Діаметр">{tire.diameter}</param>\n'
                yield f'<param name="Сезон">{season}</param>\n'
                yield '</offer>\n'

        # Disks
        if product_type in ['all', 'disks']:
            disks = Disk.objects.select_related('brand').only(
                'id', 'slug', 'price', 'in_stock', 'image',
                'brand__name', 'model_name', 'width', 'diameter',
                'bolts', 'pcd', 'et', 'dia', 'disk_type'
            )

            if supplier_ids:
                disks = disks.filter(supplier_id__in=supplier_ids)
            if in_stock_param == '1':
                disks = disks.filter(in_stock=True)
            elif in_stock_param == '0':
                disks = disks.filter(in_stock=False)

            type_map = {'alloy': 'Литий', 'steel': 'Сталевий', 'forged': 'Кований'}

            for disk in disks.iterator(chunk_size=1000):
                available = "true"
                name = f"{disk.brand.name} {disk.model_name} {disk.width}x{disk.diameter} {disk.bolts}x{disk.pcd}"
                disk_type = type_map.get(disk.disk_type, '')

                yield f'<offer id="disk_{disk.id}" available="{available}">\n'
                yield f'<url>{base_url}/disks/{disk.slug}/</url>\n'
                yield f'<price>{int(disk.price)}</price>\n'
                yield '<currencyId>UAH</currencyId>\n'
                yield '<categoryId>2</categoryId>\n'
                if disk.image:
                    yield f'<picture>{base_url}/media/{disk.image}</picture>\n'
                yield f'<name>{escape_xml(name)}</name>\n'
                yield f'<vendor>{escape_xml(disk.brand.name)}</vendor>\n'
                desc = f"Диск {name}. Тип: {disk_type}. ET: {disk.et}. DIA: {disk.dia}."
                yield f'<description>{escape_xml(desc)}</description>\n'
                yield f'<param name="Діаметр">{disk.diameter}</param>\n'
                yield f'<param name="Ширина">{disk.width}</param>\n'
                yield f'<param name="PCD">{disk.bolts}x{disk.pcd}</param>\n'
                yield f'<param name="ET">{disk.et}</param>\n'
                yield f'<param name="Тип">{disk_type}</param>\n'
                yield '</offer>\n'

        # Footer
        yield '</offers>\n'
        yield '</shop>\n'
        yield '</yml_catalog>\n'

    response = StreamingHttpResponse(generate(), content_type='application/xml; charset=utf-8')
    response['Content-Disposition'] = 'inline; filename="price.xml"'
    return response


def escape_xml(text):
    """Escape special XML characters"""
    if not text:
        return ""
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    return text
