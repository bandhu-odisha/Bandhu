// Collapse Navbar
// Add styling fallback for when a transparent background .navbar is scrolled
var navbarCollapse = function() {
    if($(".navbar.bg-transparent.fixed-top").length === 0) {
        return;
    }
    if ($(".navbar.bg-transparent.fixed-top").offset().top > 50) {
        $(".navbar").addClass("navbar-scrolled");
    }
    else {
        $(".navbar").removeClass("navbar-scrolled");
    }
    if ($(".navbar.bg-transparent.fixed-top").offset().top > 300) {
        $(".navbar").addClass("navbar-scrolled-again");
    }
    else {
        $(".navbar").removeClass("navbar-scrolled-again");
    }
};
// Collapse now if page is not at top
navbarCollapse();
// Collapse the navbar when page is scrolled
$(window).scroll(navbarCollapse);
