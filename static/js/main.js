/* main.js — search, toast, cart badge, mobile menu, modals (callback, one-click) */
(function () {
  var body = document.body;
  var csrf = body.dataset.csrf;
  var urlCartAdd = body.dataset.urlCartAdd;
  var urlCartCount = body.dataset.urlCartCount;
  var urlOneClickOrder = body.dataset.urlOneClickOrder;
  var urlCallbackRequest = body.dataset.urlCallbackRequest;

  // ─── Search toggle ──────────────────────────────────
  window.toggleSearch = function () {
    var dropdown = document.getElementById('searchDropdown');
    var input = document.getElementById('searchInput');
    dropdown.classList.toggle('active');
    if (dropdown.classList.contains('active')) {
      input.focus();
    }
  };

  // Close search when clicking outside
  document.addEventListener('click', function (e) {
    var wrapper = document.querySelector('.search-wrapper');
    var dropdown = document.getElementById('searchDropdown');
    if (wrapper && !wrapper.contains(e.target) && dropdown.classList.contains('active')) {
      dropdown.classList.remove('active');
    }
  });

  // Close search on Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      var dropdown = document.getElementById('searchDropdown');
      if (dropdown.classList.contains('active')) {
        dropdown.classList.remove('active');
      }
    }
  });

  // ─── Toast notification ─────────────────────────────
  window.showToast = function (message, type) {
    type = type || 'success';
    var toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = 'toast show ' + type;
    setTimeout(function () { toast.className = 'toast'; }, 3000);
  };

  // ─── Cart badge ─────────────────────────────────────
  window.updateCartBadge = function (count) {
    var badge = document.getElementById('cartBadge');
    if (badge) {
      badge.textContent = count;
      badge.style.display = count > 0 ? 'flex' : 'none';
    }
  };

  // ─── Add to cart ────────────────────────────────────
  window.addToCart = function (type, id, event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }

    fetch(urlCartAdd, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf
      },
      body: JSON.stringify({ type: type, id: id, quantity: 1 })
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (data.success) {
        showToast(data.message, 'success');
        updateCartBadge(data.cart_count);
      } else {
        showToast(data.error || 'Помилка', 'error');
      }
    })
    .catch(function () {
      showToast('Помилка з\'єднання', 'error');
    });
  };

  // Load cart count on page load
  document.addEventListener('DOMContentLoaded', function () {
    fetch(urlCartCount)
      .then(function (r) { return r.json(); })
      .then(function (data) { updateCartBadge(data.count); });
  });

  // ─── One Click Buy Modal ────────────────────────────
  window.openOneClickModal = function (type, productId, productName, productPrice) {
    document.getElementById('oneClickType').value = type;
    document.getElementById('oneClickProductId').value = productId;
    document.getElementById('oneClickProductInfo').innerHTML =
      '<div class="modal-product-name">' + productName + '</div>' +
      '<div class="modal-product-price">' + productPrice + ' ₴</div>';
    document.getElementById('oneClickModal').classList.add('active');
    document.body.style.overflow = 'hidden';
    document.getElementById('oneClickPhone').focus();
  };

  window.closeOneClickModal = function () {
    document.getElementById('oneClickModal').classList.remove('active');
    document.body.style.overflow = '';
    document.getElementById('oneClickForm').reset();
  };

  // Close one click modal on overlay click
  document.getElementById('oneClickModal').addEventListener('click', function (e) {
    if (e.target === this) {
      closeOneClickModal();
    }
  });

  // Handle one click form submission
  document.getElementById('oneClickForm').addEventListener('submit', function (e) {
    e.preventDefault();

    var type = document.getElementById('oneClickType').value;
    var productId = document.getElementById('oneClickProductId').value;
    var phone = document.getElementById('oneClickPhone').value.trim();

    if (!phone) {
      showToast('Введіть номер телефону', 'error');
      return;
    }

    var submitBtn = this.querySelector('.modal-submit');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Оформлюємо...';

    fetch(urlOneClickOrder, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf
      },
      body: JSON.stringify({ type: type, product_id: productId, phone: phone })
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (data.success) {
        showToast(data.message, 'success');
        closeOneClickModal();
      } else {
        showToast(data.error || 'Помилка оформлення', 'error');
      }
    })
    .catch(function () {
      showToast('Помилка з\'єднання', 'error');
    })
    .finally(function () {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Замовити';
    });
  });

  // ─── Callback Modal ─────────────────────────────────
  window.openCallbackModal = function () {
    document.getElementById('callbackModal').classList.add('active');
    document.body.style.overflow = 'hidden';
  };

  window.closeCallbackModal = function () {
    document.getElementById('callbackModal').classList.remove('active');
    document.body.style.overflow = '';
    document.getElementById('callbackForm').reset();
  };

  // Close modal on overlay click
  document.getElementById('callbackModal').addEventListener('click', function (e) {
    if (e.target === this) {
      closeCallbackModal();
    }
  });

  // Close modals on Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      var callbackModal = document.getElementById('callbackModal');
      var oneClickModal = document.getElementById('oneClickModal');
      if (callbackModal.classList.contains('active')) {
        closeCallbackModal();
      }
      if (oneClickModal.classList.contains('active')) {
        closeOneClickModal();
      }
    }
  });

  // Handle callback form submission
  document.getElementById('callbackForm').addEventListener('submit', function (e) {
    e.preventDefault();

    var name = document.getElementById('callbackName').value.trim();
    var phone = document.getElementById('callbackPhone').value.trim();
    var question = document.getElementById('callbackQuestion').value.trim();

    if (!name || !phone) {
      showToast('Заповніть обов\'язкові поля', 'error');
      return;
    }

    var submitBtn = this.querySelector('.modal-submit');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Надсилаємо...';

    fetch(urlCallbackRequest, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf
      },
      body: JSON.stringify({ name: name, phone: phone, question: question })
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (data.success) {
        showToast(data.message, 'success');
        closeCallbackModal();
      } else {
        showToast(data.error || 'Помилка відправки', 'error');
      }
    })
    .catch(function () {
      showToast('Помилка з\'єднання', 'error');
    })
    .finally(function () {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Надіслати';
    });
  });

  // ─── Mobile Menu ────────────────────────────────────
  var mobileToggle = document.getElementById('mobileMenuToggle');
  var mobileOverlay = document.getElementById('mobileMenuOverlay');
  var mobileClose = document.getElementById('mobileMenuClose');

  function openMobileMenu() {
    mobileOverlay.classList.add('active');
    mobileToggle.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeMobileMenu() {
    mobileOverlay.classList.remove('active');
    mobileToggle.classList.remove('active');
    document.body.style.overflow = '';
  }

  mobileToggle.addEventListener('click', openMobileMenu);
  mobileClose.addEventListener('click', closeMobileMenu);
  mobileOverlay.addEventListener('click', function (e) {
    if (e.target === this) closeMobileMenu();
  });
})();
