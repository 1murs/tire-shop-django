function whatIsOffset() {
    alert("Offset is a position of a wheel's dish inside of the rim.\nLower offset - deeper the dish and accordingly - wider wheel's lips.");
}

function isNormalLanguage(val) {
    val = val.toLowerCase();
    if (val == null || val.length <= 0)
        return true;
    if (val.indexOf("fuck") >= 0) return false;
    if (val.indexOf("shit") >= 0) return false;
    return true;
}

function validateIsNormalLanguage(aField, aTitle) {
    if (!isNormalLanguage(aField.value)) {
        alert("This is a public site.\nFilter your language please.");
        aField.focus();
        return false;
    }
    return true;
}


function trimString(aValue) {  // Returns new value without lead and tail spaces
    var val = new String(aValue);
    if (val == null)
        val = "";
    if (val.length > 0)
        while (val.length > 0 && val.charAt(0) == ' ')
            val = val.substring(1, val.length);
    if (val.length > 0)
        while (val.length > 0 && val.charAt(val.length - 1) == ' ')
            val = val.substring(0, val.length - 1);
    return (val);
}

function validateNotEmpty(aField, aTitle) {
    val = aField.value;
    if (val == null || trimString(val) == "") {
        if (aTitle == null)
            aTitle = "Field";
        alert(aTitle + " is required.");
        aField.focus();
        return false;
    }
    return true;
}

function isNumber(val) {
    if (val == null || trimString(val) == "")
        return true;
    if (val.charAt(0) == '-')
        val = val.substring(1, val.length);
    pointPos = -1;
    ret = true;
    for (i = 0; i < val.length; i++) {
        ch = val.charAt(i);
        if (ch == ',' && pointPos >= 0) {
            ret = false;
            break;
        } else if (ch == '.') {
            if (pointPos < 0)
                pointPos = i;
            else {
                ret = false;
                break;
            }
        } else if (ch < '0' || ch > '9') {
            ret = false;
            break;
        }
    }
    if (!ret) {
        return false;
    }
    return true;
}

function validateIsNumber(aField, aTitle) {
    aField.value = trimString(aField.value);
    var val = new String(aField.value);
    if (!isNumber(val)) {
        if (aTitle == null)
            aTitle = "";
        alert(aTitle + " should be a number.")
        aField.focus();
        return false;
    }
    return true;
}

function isNormalString(val) {
    sRef = "'\"<>&%";
    var ret = true;
    var cTemp = ' ';
    if (val == null || val.length <= 0)
        return true;
    for (i = 0; i < sRef.length; i++) {
        cTemp = sRef.substring(i, i + 1);
        if (val.indexOf(cTemp) >= 0) {
            ret = false;
            break;
        }
    }
    return ret;
}

function validateIsNormalString(aField, aTitle) {
    sRef = "' \" < > & %";
    if (!isNormalString(aField.value)) {
        if (aTitle == null)
            alert("Please avoid using special symbols such as " + sRef);
        else
            alert("Please avoid using special symbols such as " + sRef + " in the " + aTitle);
        aField.focus();
        return false;
    }
    return true;
}

function isEmail(val) {
    if (val == null || val == "")
        return true;
    val = trimString(val);
    if (!isNormalString(val))
        return false;
    stillvalid = true;

    if (stillvalid) {
        pos = val.indexOf("www.");
        if (pos == 0) {
            stillvalid = false;
        }
    }

    if (stillvalid) {
        pos = val.indexOf('@');
        if (pos <= 0)
            stillvalid = false;
    }
    if (stillvalid) {
        val = val.substring(pos + 1, val.length); //cut up to '@'
        pos = val.indexOf('.');
        if (pos <= 0)
            stillvalid = false;
    }
    return stillvalid;
}

function validateIsEmail(fieldObj, fieldLabel) {
    fieldObj.value = trimValue(fieldObj.value);
    val = fieldObj.value;
    stillvalid = isEmail(val);
    if (stillvalid)
        return true;
    else {
        if (fieldLabel == null)
            alert("Invalid email.");
        else
            alert("Please enter valid " + fieldLabel + ".");
        fieldObj.focus();
        return false;
    }
}

function pickDigits(inStr) {
    var c;
    var outStr = "";
    for (i = 0; i < inStr.length; i++) {
        c = inStr.substring(i, i + 1);
        if (c >= '0' && c <= '9')
            outStr += c;
    }
    return outStr;
}

function countDigits(inStr) {
    return pickDigits(inStr).length;
}

function convertDateFormat(inString, outFormat) { //returns null or correct format
    if (inString.length == 0)
        return null;
    var n = 0;
    var s0 = "";
    var s1 = "";
    var s2 = "";
    for (i = 0; i < inString.length; i++) {
        dateChar = inString.substring(i, i + 1);
        if (dateChar != ' ') {
            if (dateChar >= '0' && dateChar <= '9') {
                if (n == 0)
                    s0 += dateChar;
                else if (n == 1)
                    s1 += dateChar;
                else if (n == 2)
                    s2 += dateChar;
                else
                    return null;
            } else //switch to next subfiels
                n++;
        }
    }
    if (s0.length() == 4) {
        yy = 1 * s0;
        mm = 1 * s1;
        dd = 1 * s2;
    } else {
        mm = 1 * s0;
        dd = 1 * s1;
        yy = 1 * s2;
        if (yy < 100) {
            if (yy > 50)
                yy += 1900;
            else
                yy += 2000;
        }
    }
    if (mm < 1 || mm > 12)
        return null;
    if (yy < 1 || yy > 9999)
        return null;
    if (dd < 1 || dd > 31)
        return null;

    if (dd > 30 && (mm == 2 || mm == 4 || mm == 6 || mm == 9 || mm == 11))
        return null;
    if (mm == 2) {
        if (yy % 4 == 0) {
            if (dd > 29)
                return null;
        } else if (dd > 28)
            return null;
    }
    sMM = "";
    if (mm < 10)
        sMM += "0";
    sMM += mm;
    sDD = "";
    if (dd < 10)
        sDD += "0";
    sDD += dd;
    sYY = yy;

    if (outFormat.indexOf("YYYY") == 0)  // YYYY-MM-DD
        outString = "" + sYY + "-" + sMM + "-" + sDD;
    else         // MM/DD/YYYY
        outString = "" + sMM + "/" + sDD + "/" + sYY;

    return outString;
}

function todaysDate() { //returns current date in string format
    var curDate = new Date();
    var mm = curDate.getMonth() + 1;
    var dd = curDate.getDate();
    var yy = curDate.getYear();

    if (yy < 100) {
        if (yy > 50)
            yy += 1900;
        else
            yy += 2000;
    }
    sMM = "";
    if (mm < 10)
        sMM += "0";
    sMM += mm;
    sDD = "";
    if (dd < 10)
        sDD += "0";
    sDD += dd;
    sYY = yy;
    var outString = sMM + "/" + sDD + "/" + sYY;
    return outString;
}

function validateIsDate(aField, aTitle) {
    if (aField.value == "")
        return true;
    correctedDateString = convertDateFormat(aField.value, "MM/DD/YYYY");
    if (correctedDateString == null) {
        if (aTitle == null)
            aTitle = "";
        alert(aTitle + " wrong DATE. Expected format is MM/DD/YYYY or MM/DD/YY or YYYY-MM-DD.");
        aField.value = todaysDate();
        aField.focus();
        return false;
    }
    aField.value = correctedDateString;
    return true;
}


function translateString(inStr, inSeq, outSeq) {
    while (inStr.indexOf(inSeq) >= 0)
        inStr = inStr.replace(inSeq, outSeq);
    return inStr;
}

function resizeParentFrame() {
    if (parent == null) return;
    d = parent.document;
    if (d.all == null) return;
    for (i = 0; i < d.all.length; i++) {
        el = d.all[i];
        if (el.tagName != null)
            if (el.tagName == 'iframe' || el.tagName == 'IFRAME') {
                el.height = document.body.scrollHeight;
                el.width = document.body.scrollWidth;
                el.scrolling = "no";
                return;
            }
    }
}

function selectValue(el) {
    return el.options[el.selectedIndex].value;
}

function setSelect(el, value) {
    for (i = 0; i < el.options.length; i++) {
        if (el.options[i].value == value) {
            el.selectedIndex = i;
            return i;
        }
    }
    return -1;
}

///////////////////////
//OLD SET


/* 
 * Sets focus to field.
 * Params:
 *   fieldObj   - target input field
 *   fieldLabel - null if use in blur event
 *                (Netscape problem fixes)
 * Returns:
 *   none
 */
function setFocus(fieldObj, fieldLabel) {
    if ((navigator.appName != "Microsoft Internet Explorer") && (fieldLabel == null))
        fieldObj.value = "";
    fieldObj.focus();
}

function var2zero4Netscape(fieldObj) {
    if (navigator.appName.indexOf("Microsoft") < 0)
        fieldObj.value = "0";
}

/* 
 * Trims a string.
 * Params:
 *   aValue  - string to trim
 * Returns:
 *   new value without lead and tail spaces
 */
function trim(aValue) {
    var val = new String(aValue);
    if (val == null) {  // it never happens
        val = "";
    }
    while (val.length > 0 && val.charAt(val.length - 1) == ' ') {
        val = val.substring(0, val.length - 1);
    }
    return (val);
}

/*
 *  Validates required field.
 *  Trims value string before validation 
 *  You cannot use it with blur event (Netscape problem)
 *  Params:
 *    fieldObj   input field itself
 *    fieldLabel GUI fieldLabel of input field
 *  Returns:
 *    true if value OK, false if value empty 
 */
function validateRequired(fieldObj, fieldLabel) {
    ret = true;
    var val = trim(fieldObj.value);
    if (val.length <= 0) {
        ret = false;
    }
    if (!ret) {
        fieldObj.value = trim(fieldObj.value);
        if (fieldLabel == null) {
            alert("Field is required");
        } else {
            alert(fieldLabel + " is required");
        }
        fieldObj.focus();
    }
    return (ret);
}


/*
 *  Validates Numeric field.
 *  For float numbers use validateFloatString
 *  Maximum number is 99999999
 *  Params:
 *    fieldObj   input field itself
 *    fieldLabel GUI fieldLabel of input field. String
 *               or null when used in blur event.
 *  Returns:
 *    true if value OK, false if value is not a number
 */
function validateNumericString(fieldObj, fieldLabel) {
    var ret = validateNumericStringValue(fieldObj.value);

    if (!ret) {
        if (fieldLabel == null) {
            alert("Should be a number!");
        } else {
            alert(fieldLabel + " should be a number!");
        }
    }
    if (!ret) {
        setFocus(fieldObj, fieldLabel);
    }
    return (ret);
}

function validateNumericStringValue(val) {
    RefString = "1234567890";
    var ret = true;
    if (val.length > 0) {
        for (i = 0; i < val.length; i++) {
            TempChar = val.substring(i, i + 1);
            if (RefString.indexOf(TempChar, 0) < 0) {
                ret = false;
                break;
            }
        }
    }
    return (ret);
}


/*
 *  Validates Float Numeric field.
 *  For long numbers use validateNumericString
 *  Maximum number is 99999999.99
 *  Allows commas before point
 *  Params:
 *    fieldObj   input field itself
 *    fieldLabel GUI fieldLabel of input field. String
 *               or null when used in blur event.
 *  Returns:
 *    true if value OK, false if value is not a number
 */
function validatePositiveFloatString(fieldObj, fieldLabel) {
    if (!validateFloatString(fieldObj, fieldLabel))
        return false;
    if (fieldObj.value < 0) {
        if (fieldLabel == null) {
            alert("Should be positive number.");
        } else {
            alert(fieldLabel + " cannot have negative value.");
        }
        //fieldObj.value="0"
        setFocus(fieldObj, fieldLabel);
        return false;
    }
    return true;
}

function validateFloatString(fieldObj, fieldLabel) {

    RefString = "1234567890.,";
    var ret = true;
    var val = new String(fieldObj.value);
    var countBeforeDecimal = 0;
    var count = 0;
    var index = -1;

    if (val.length > 0) {
        // validate format...
        index = val.indexOf('.', 0);
        if (index >= 0 && index < val.length - 1) {
            if (val.indexOf('.', index + 1) >= 0
                || val.indexOf(',', index + 1) >= 0) {
                ret = false;
            }
        }
        // validate chars, calulate number of digits
        for (i = 0; i < val.length && ret; i++) {
            TempChar = val.substring(i, i + 1);
            if (RefString.indexOf(TempChar, 0) < 0) {
                ret = false;
                break;
            }
            if (TempChar != ',' && TempChar != '.') {
                if (index < 0 || i < index) {
                    countBeforeDecimal++;
                }
                count++;
            }
        }
        if (!ret || count <= 0) {
            fieldObj.focus();
            if (fieldLabel == null) {
                alert("Should be a number!");
            } else {
                alert(fieldLabel + " should be a number!");
            }
            ret = false;
        }
        if (ret && countBeforeDecimal > 8) {
            fieldObj.focus();
            if (fieldLabel == null) {
                alert("Maximum allowed number is 99,999,999.99!");
            } else {
                alert(fieldLabel + " cannot be more then 99,999,999.99!");
            }
            ret = false;
        }
    }


    if (!ret) {
        setFocus(fieldObj, fieldLabel);
    }
    return (ret);

}

function validateMoneyString(fieldObj, fieldLabel) {
    if (!validatePositiveFloatString(fieldObj, fieldLabel))
        return false;
    var outstr = formatMoneyString(fieldObj.value);
    fieldObj.value = outstr;
    return true;
}

function formatMoneyString(val) {
    var num = parseFloat(val) + 0.005;
    val = "" + num;
    val = val.substring(0, val.indexOf('.') + 3);
    return formatFloatString(val);
}


function formatFloatString(val) {
    var pointpos = val.indexOf('.');
    var decpart = "";
    var intpart = val;
    if (pointpos >= 0) {
        decpart = val.substring(pointpos + 1, val.length);
        intpart = val.substring(0, pointpos);
    }
    decpart = pickDigits(decpart);
    intpart = pickDigits(intpart);

    var c;
    //cut front 00
    while (intpart.length > 1) {
        c = intpart.substring(0, 1);
        if (c == "0")
            intpart = intpart.substring(1, intpart.length);
        else
            break;
    }
    if (intpart.length <= 0)
        intpart = "0";

    var outstr = intpart;
    if (decpart.length > 0)
        outstr += ("." + decpart);
    return outstr;
}

/*
 *  Validates String for quotes and tag usage
 *  Params:
 *    fieldObj   input field itself
 *    fieldLabel GUI fieldLabel of input field. String
 *               or null when used in blur event.
 *  Returns:
 *    true if value OK, false if value contains quotes or tags
 */
function validateString(fieldObj, fieldLabel) {
    var ret = validateStringValue(fieldObj.value, fieldLabel);
    if (!ret)
        setFocus(fieldObj, fieldLabel);
    return (ret);
}

function validateStringValue(val, fieldLabel) {
    sRef = "'\"<>&";
    var ret = true;
    var cTemp = ' ';
    if (val == null || val.length <= 0)
        return true;
    for (i = 0; i < sRef.length; i++) {
        cTemp = sRef.substring(i, i + 1);
        if (val.indexOf(cTemp, 0) >= 0) {
            ret = false;
            break;
        }
    }
    if (!ret) {
        if (fieldLabel == null)
            alert("Character " + cTemp + " is not allowed!");
        else
            alert(fieldLabel + " does not allow character " + cTemp + "!");
        return false;
    }
    return true;
}


/*
 *  Validates String Size 
 *  Params:
 *    fieldObj   input field itself
 *    fieldLabel GUI fieldLabel of input field. String
 *               or null when used in blur event.
 *    fieldSize  max size of string. Number
 *  Returns:
 *    true if value OK, false if size of string more then given
 */
function validateSizeString(fieldObj, fieldLabel, fieldSize) {
    var ret = true;
    var val = new String(fieldObj.value);
    if (val.length > fieldSize) {
        if (fieldLabel == null) {
            alert("Number of characters more then " + fieldSize + "!");
        } else {
            alert(fieldLabel + " does not allow more then " + fieldSize + " characters!");
        }
        ret = false;
        if (navigator.appName == "Netscape")
            fieldObj.value = val.substring(0, fieldSize - 1);
        //setFocus(fieldObj,fieldLabel);
        fieldObj.focus();
    }
    return (ret);

}

function validateStringAndSize(fieldObj, fieldLabel, fieldSize) {
    if (!validateString(fieldObj, fieldLabel))
        return false;
    if (!validateSizeString(fieldObj, fieldLabel, fieldSize))
        return false;
    return true;
}

/*
 *  Validates Date field.
 *  Allows format string "mm/dd/yy"
 *  Params:
 *    fieldObj   input field itself
 *    fieldLabel GUI fieldLabel of input field
 *               or null when used in blur event.
 *  Returns:
 *    true if value OK, false if value is not a date
 */

/*
 *  TBD: Validates timestamp field.
 *  Allows format string "mm/dd/yy hh:mm:ss"
 *  Params:
 *    fieldObj   input field itself
 *    fieldLabel GUI fieldLabel of input field
 *               or null when used in blur event.
 *  Returns:
 *    true if value OK, false if value is not a date
 */

function openSupport(url) {
    url = encodeURL(url);
    win_1 = open(url, "support", "resizable=yes,menubar=yes,toolbar=yes,location=no,scrollbars=yes,status=yes");
    win_1.focus();
}

var reExpArray = new Array(/\!/g, /\@/g, /\#/g, /\$/g, /\^/g, /\&/g, /\(/g, /\)/g, /\'/g, /\`/g, /~/g, /\s+/g, /\t+/g, /\:/g);
var replChars = new Array("%21", "%40", "%23", "%24", "%5E", "%26", "%28", "%29", "%27", "%60", "%7E", "%20", "%09", "%3A");

function encodeURL(value) {
    value = trimValue(value);
    if ("" != value) {
        for (var i = 0; i < reExpArray.length; i++) {
            value = value.replace(reExpArray[i], replChars[i]);
        }
    }
    return value;
}

function trimValue(value) {
    expression1 = /^\s+/g; //0 or more leading spaces
    expression2 = /\s+$/g; //0 or more trailing spaces
    replexp = "";
    if (null != value && ("" != value)) {
        value = value.replace(expression1, replexp);
        value = value.replace(expression2, replexp);
    } else {
        value = new String("");
    }
    return value;
}


function days(inString0) {   //converts date string to number of days from year 0000, assumes that string is correct
    inString = correctDateString(inString0);
    if (inString == null) {
        alert("Wrong date value: [" + inString0 + "].\nExpected format is MM/DD/YY or MM/DD/YYYY.");
        return -1;
    }
    var n = 0;
    var sMM = "";
    var sDD = "";
    var sYY = "";
    for (i = 0; i < inString.length; i++) {
        dateChar = inString.substring(i, i + 1);
        if (dateChar != ' ') {
            if (dateChar >= '0' && dateChar <= '9') {
                if (n == 0)
                    sMM += dateChar;
                else if (n == 1)
                    sDD += dateChar;
                else if (n == 2)
                    sYY += dateChar;
            } else //switch to next subfiels
                n++;
        }
    }
    var mm = Math.floor(sMM);
    var dd = Math.floor(sDD);
    if (sYY == "00")
        sYY = "2000";
    var yy = Math.floor(sYY);

    if (yy < 100) {
        if (yy > 20)
            yy += 1900;
        else
            yy += 2000;
    }
    var totalDays = yy * 365 + (yy / 4) - (yy / 100);
    for (i = 1; i <= mm; i++) {
        if (i == 2) { //feb
            if (yy % 4 == 0 && yy % 100 != 0)
                totalDays += 29;
            else
                totalDays += 28;
        } else if (i == 2 || i == 4 || i == 6 || i == 9 || i == 11)
            totalDays += 30;
        else
            totalDays += 31;
    }
    totalDays += dd;
    return totalDays;
}

function dateToDays(dateString) {
    dateString = convertDateFormat(dateString, "YYYY-MM-DD");
    if (dateString == null)
        return -1;
    yy = 1 * dateString.substring(0, 4);
    mm = 1 * dateString.substring(5, 7);
    dd = 1 * dateString.substring(8, 10);

    days = 0;
    if (yy > 1)
        for (i = yy - 1; i > 0; i--) {
            days += 365;
            if (i % 4 == 0 && i % 100 != 0)
                days++;
        }
    if (mm > 1)
        for (i = mm - 1; i > 0; i--) {
            if (i == 2) {
                //february
                if (yy % 4 == 0 && yy % 100 != 0)
                    days += 29;
                else
                    days += 28;
            } else if (i % 2 == 0)
                days += 30;
            else
                days += 31;
        }
    days += dd;
    return days;
}

