function goBack() {
    // กลับไปหน้าก่อนหน้า
    window.history.back();
}

function goNext() {
    // นำทางไปยังหน้าถัดไป (เปลี่ยน URL ตามความเหมาะสม)
    window.location.href = "next-page.html"; // แก้ไข "next-page.html" เป็นหน้าที่คุณต้องการ
}
