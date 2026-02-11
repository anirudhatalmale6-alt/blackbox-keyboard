/* On-Screen Keyboard for 7" Touchscreen (480x800) */
(function() {
    var activeInput = null;
    var shiftActive = false;

    var kbOverlay = document.createElement('div');
    kbOverlay.id = 'osk-overlay';
    kbOverlay.style.cssText = 'display:none;position:fixed;bottom:0;left:0;width:100%;z-index:9999;background:#111;border-top:2px solid #c00;padding:5px;box-sizing:border-box;';

    var rows = [
        ['1','2','3','4','5','6','7','8','9','0'],
        ['Q','W','E','R','T','Y','U','I','O','P'],
        ['A','S','D','F','G','H','J','K','L','@'],
        ['SHIFT','Z','X','C','V','B','N','M','.','DEL'],
        ['SPACE','DONE']
    ];

    var kbHTML = '';
    for (var r = 0; r < rows.length; r++) {
        kbHTML += '<div style="display:flex;gap:3px;margin-bottom:3px;justify-content:center;">';
        for (var k = 0; k < rows[r].length; k++) {
            var key = rows[r][k];
            var w = '9%'; var fs = '14px';
            if (key === 'SPACE') { w = '60%'; }
            else if (key === 'DONE') { w = '35%'; }
            else if (key === 'SHIFT') { w = '14%'; fs = '11px'; }
            else if (key === 'DEL') { w = '14%'; fs = '11px'; }
            var bgColor = '#222'; var borderColor = '#600'; var textColor = '#fff';
            if (key === 'DONE') { bgColor = '#030'; borderColor = '#0c0'; textColor = '#0c0'; }
            else if (key === 'DEL') { bgColor = '#300'; borderColor = '#c00'; textColor = '#c00'; }
            else if (key === 'SHIFT') { bgColor = '#220'; borderColor = '#660'; textColor = '#fc0'; }
            var label = key;
            if (key === 'SPACE') label = 'SPATIE';
            else if (key === 'DEL') label = 'WISSEN';
            else if (key === 'DONE') label = 'KLAAR';
            else if (key === 'SHIFT') label = 'A/a';
            kbHTML += '<button type="button" data-key="' + key + '" style="width:' + w + ';height:42px;background:' + bgColor + ';border:1px solid ' + borderColor + ';color:' + textColor + ';font-size:' + fs + ';font-weight:bold;border-radius:4px;touch-action:manipulation;-webkit-user-select:none;user-select:none;">' + label + '</button>';
        }
        kbHTML += '</div>';
    }
    kbOverlay.innerHTML = kbHTML;
    document.body.appendChild(kbOverlay);

    function pressKey(key) {
        if (!activeInput) return;
        if (key === 'DONE') { hideKeyboard(); return; }
        if (key === 'DEL') { activeInput.value = activeInput.value.slice(0, -1); fireInput(); return; }
        if (key === 'SHIFT') { shiftActive = !shiftActive; updateShiftDisplay(); return; }
        if (key === 'SPACE') { activeInput.value += ' '; }
        else { activeInput.value += shiftActive ? key.toUpperCase() : key.toLowerCase(); }
        fireInput();
    }

    function fireInput() {
        if (!activeInput) return;
        var evt = new Event('input', { bubbles: true });
        activeInput.dispatchEvent(evt);
    }

    kbOverlay.addEventListener('touchstart', function(e) {
        var btn = e.target.closest('button');
        if (btn) { e.preventDefault(); e.stopPropagation(); pressKey(btn.getAttribute('data-key')); }
    }, { passive: false });

    kbOverlay.addEventListener('mousedown', function(e) {
        var btn = e.target.closest('button');
        if (btn) { e.preventDefault(); e.stopPropagation(); pressKey(btn.getAttribute('data-key')); }
    });

    function updateShiftDisplay() {
        var btns = kbOverlay.querySelectorAll('button');
        for (var i = 0; i < btns.length; i++) {
            var key = btns[i].getAttribute('data-key');
            if (key && key.length === 1 && key.match(/[A-Z]/)) {
                btns[i].textContent = shiftActive ? key.toUpperCase() : key.toLowerCase();
            }
        }
        var shiftBtn = kbOverlay.querySelector('[data-key="SHIFT"]');
        if (shiftBtn) { shiftBtn.style.background = shiftActive ? '#440' : '#220'; }
    }

    function showKeyboard(input) {
        activeInput = input;
        kbOverlay.style.display = 'block';
    }

    function hideKeyboard() {
        kbOverlay.style.display = 'none';
        activeInput = null;
    }

    function attachToInputs() {
        var inputs = document.querySelectorAll('input[type="text"], input[type="password"]');
        for (var i = 0; i < inputs.length; i++) {
            inputs[i].setAttribute('inputmode', 'none');
            inputs[i].addEventListener('touchstart', function(e) { e.preventDefault(); showKeyboard(this); this.focus(); }, { passive: false });
            inputs[i].addEventListener('mousedown', function(e) { e.preventDefault(); showKeyboard(this); this.focus(); });
        }
    }

    document.addEventListener('touchstart', function(e) {
        if (kbOverlay.style.display === 'block' && !kbOverlay.contains(e.target) && (!activeInput || e.target !== activeInput)) {
            hideKeyboard();
        }
    });

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', attachToInputs); }
    else { attachToInputs(); }
    updateShiftDisplay();
})();
