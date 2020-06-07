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


// Close Navbar on clicking outside it
$(window).on('click', function(event){
    var clickOver = $(event.target)
    console.log(clickOver.closest('.navbar').length)
    if ($('.navbar .navbar-toggler').attr('aria-expanded') == 'true' && !(clickOver.closest('.navbar').length === 1)) {
        $('button[aria-expanded="true"]').click();
    }
});


// ON PAGE NAVIGATION
$(document).ready(function(){
    // Select all links with hashes
    $('a[href*="#"]')
        // Remove links that don't actually link to anything
        .not('[href="#"]')
        .not('[href="#0"]')
        .click(function(event) {
        // On-page links
        if (
            location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') 
            && 
            location.hostname == this.hostname
        ) {
            // Figure out element to scroll to
            var hash = this.hash
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
            // Does a scroll target exist?
            if (target.length) {
                // Only prevent default if animation is actually gonna happen
                event.preventDefault();
                // Close Navbar
                $('button[aria-expanded="true"]').click();
                // Scroll to target
                $('html, body').animate({
                    scrollTop: target.offset().top
                }, 1000, function() {
                    // Callback after animation
                    // Must change focus!
                    // var $target = $(target);
                    // $target.focus();
                    // if ($target.is(":focus")) { // Checking if the target was focused
                    //     return false;
                    // }
                    // else {
                    //     // $target.attr('tabindex','-1'); // Adding tabindex for elements not focusable
                    //     $target.focus(); // Set focus again
                    // };

                    window.location.hash = hash;
                });
            }
        }
    });

    // SCROLL TO TOP BUTTON
    $(window).scroll(function() {
        if ($(this).scrollTop() > 200) {
            $('#scroll-to-top').fadeIn('slow');
        } 
        else {
            $('#scroll-to-top').fadeOut('slow');
        }
    }); 
    $('#scroll-to-top').click(function(){
        $("html,body").animate({ scrollTop: 0 }, 1000);
        return false;
    });

});

// CONTACT SCROLLSPY PROBLEM
function contact_scrollspy(){
    $(window).scroll(function(){
        let bottom = $(document).height() - $(window).height() - $(window).scrollTop()
        // console.log(bottom);
        if (bottom < 2) {
            $('[data-spy="scroll"]').scrollspy('dispose');
            $('.navbar .navbar-nav li .nav-link.active').removeClass('active');
            $('[href="#contact"]').addClass('active');
        }
        else if (bottom < 250) {
            $('[data-spy="scroll"]').scrollspy('dispose');
            $('.navbar .navbar-nav li .nav-link.active').removeClass('active');
            $('[data-spy="scroll"]').scrollspy('refresh');
        }
    })
}
