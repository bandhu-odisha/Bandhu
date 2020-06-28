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
    if ($('.navbar .navbar-toggler').attr('aria-expanded') == 'true' && clickOver.closest('.navbar').length === 0) {
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


// ISOTOPE FILTERING

$(document).ready(function() {
    "use strict";
  
    /*--------------------- Gallery Item Filter-----------------*/
    var $container = $('.gallery-item'),
    colWidth = function () {
        var w = $container.width(), 
        columnNum = 1,
        columnWidth = 0;
        if (w > 960) {
            columnNum  = 4;
        }
        else if (w > 768) {
            columnNum  = 3;
        }
        else if (w > 480) {
            columnNum  = 2;
        }
        columnWidth = Math.floor(w/columnNum);
        $container.find('.item').each(function() {
            var $item = $(this),
            multiplier_w = $item.attr('class').match(/item-w(\d)/),
            multiplier_h = $item.attr('class').match(/item-h(\d)/),
            width = multiplier_w ? columnWidth*multiplier_w[1]-10 : columnWidth-10,
            height = multiplier_h ? columnWidth*multiplier_h[1]*0.7-10 : columnWidth*0.7-10;
            $item.css({
                width: width,
                height: height
            });
        });
        return columnWidth;
    },
    isotope = function () {
        $container.isotope({
            resizable: true,
            itemSelector: '.item',
            masonry: {
                columnWidth: colWidth(),
                gutterWidth: 10
            }
        });
    };
    isotope();
    $(window).resize(isotope);
  
    $('.galleryFilter a').click(function(){
        $('.galleryFilter .current').removeClass('current');
        $(this).addClass('current');

        var selector = $(this).attr('data-filter');
        $container.isotope({
            filter: selector,
            animationOptions: {
                duration: 750,
                easing: 'linear',
                queue: false
            }
        });
        return false;
    });

    //****************************
    // Isotope Load more button
    //****************************
    var initShow = 3; //number of items loaded on init & onclick load more button
    var next_show = 4;
    var counter = initShow; //counter for load more button
    var iso = $container.data('isotope'); // get Isotope instance
  
    loadMore(initShow); //execute function onload
  
    function loadMore(toShow) {
      $container.find(".hidden").removeClass("hidden");
  
      var hiddenElems = iso.filteredItems.slice(toShow, iso.filteredItems.length).map(function(item) {
        return item.element;
      });
      $(hiddenElems).addClass('hidden');
      $('#load-more').removeClass("hidden");
  
      //when no more to load, hide show more button
      if (hiddenElems.length <= 1) {  // Hidden elements will also contain #load-more
        jQuery("#load-more").hide();
      } else {
        jQuery("#load-more").show();
      };

      $container.isotope('layout');
  
    }
  
    //append load more button
    // $container.after('<button id="load-more"> Load More</button>');
  
    //when load more button clicked
    $("#load-more").click(function() {
      if ($('.galleryFilter').data('clicked')) {
        //when filter button clicked, set initial value for counter
        counter = initShow;
        $('.galleryFilter').data('clicked', false);
      } else {
        counter = counter;
      };
  
      counter = counter + next_show;
  
      loadMore(counter);
    });
  
    //when filter button clicked
    $(".galleryFilter a").click(function() {
      $(this).parent().data('clicked', true);

      loadMore(initShow);
    });
  
});
