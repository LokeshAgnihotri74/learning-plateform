document.addEventListener("DOMContentLoaded", function () {
    // Select all navigation links with the 'admin-tab' class
    const tabs = document.querySelectorAll(".admin-tab");
    // Select all display panels with the 'admin-section' class
    const sections = document.querySelectorAll(".admin-section");

    tabs.forEach(tab => {
        tab.addEventListener("click", function (e) {
            // Prevent default jump action of empty anchor links
            e.preventDefault();

            // 1. Remove active status highlighting from all dashboard links
            tabs.forEach(t => t.classList.remove("active"));
            
            // 2. Hide all layout panel content views 
            sections.forEach(s => s.classList.remove("active-section"));

            // 3. Highlight the specific tab that was clicked
            this.classList.add("active");
            
            // 4. Extract the target section ID and make it visible
            const targetId = this.getAttribute("data-target");
            const targetSection = document.getElementById(targetId);
            
            if (targetSection) {
                targetSection.classList.add("active-section");
            }
        });
    });
});