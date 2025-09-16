function goToPage(page) {
    // ซ่อนทุกหน้า
    const pages = document.querySelectorAll('.page');
    pages.forEach(p => p.classList.remove('active'));
    
    // แสดงหน้าที่ต้องการ
    const targetPage = document.querySelector(`.${page}`);
    if (targetPage) {
        targetPage.classList.add('active');
    }
}

// เริ่มต้นที่หน้า landing
document.addEventListener('DOMContentLoaded', function() {
    goToPage('landing');
});