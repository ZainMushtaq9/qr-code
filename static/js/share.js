/**
 * Share utilities — WhatsApp share, copy link, Web Share API, download
 */

function showToast(msg) {
    const t = document.getElementById('toast');
    if (!t) return;
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2500);
}

function downloadQR(base64, filename) {
    const a = document.createElement('a');
    a.href = 'data:image/png;base64,' + base64;
    a.download = filename || `qr-code-${Date.now()}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showToast('✅ QR Code downloaded!');
}

function downloadQRasPDF(base64, filename) {
    // Simple PDF with embedded image
    const img = new Image();
    img.onload = function () {
        const canvas = document.createElement('canvas');
        canvas.width = 595;  // A4 width in points at 72dpi
        canvas.height = 842; // A4 height
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, 595, 842);
        // Center QR at 400x400 on page
        const qrSize = 400;
        const x = (595 - qrSize) / 2;
        const y = 120;
        ctx.drawImage(img, x, y, qrSize, qrSize);
        // Title
        ctx.fillStyle = '#333';
        ctx.font = 'bold 24px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('QR Code Studio', 297, 60);
        ctx.font = '14px Inter, sans-serif';
        ctx.fillText('Generated at qrcodestudio.com', 297, 85);
        ctx.fillText('Scan this QR code with your phone camera', 297, y + qrSize + 40);
        // Convert to blob & download
        canvas.toBlob(blob => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = (filename || 'qr-code') + '.png'; // Canvas gives PNG, true PDF needs a library
            a.click();
            URL.revokeObjectURL(url);
        });
    };
    img.src = 'data:image/png;base64,' + base64;
    showToast('✅ PDF-ready image downloaded!');
}

function shareOnWhatsApp(text) {
    const url = `https://wa.me/?text=${encodeURIComponent(text || 'Check out this QR Code generator: ' + window.location.href)}`;
    window.open(url, '_blank');
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('✅ Copied to clipboard!');
    }).catch(() => {
        // Fallback
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showToast('✅ Copied!');
    });
}

function shareNative(title, text) {
    if (navigator.share) {
        navigator.share({ title, text, url: window.location.href }).catch(() => { });
    } else {
        copyToClipboard(window.location.href);
    }
}
