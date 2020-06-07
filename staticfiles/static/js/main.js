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
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
            // Does a scroll target exist?
            if (target.length) {
                // Only prevent default if animation is actually gonna happen
                event.preventDefault();
                $('html, body').animate({
                    scrollTop: target.offset().top - 75
                }, 1000, function() {
                    // Callback after animation
                    // Must change focus!
                    var $target = $(target);
                    $target.focus();
                    if ($target.is(":focus")) { // Checking if the target was focused
                        return false;
                    }
                    else {
                        // $target.attr('tabindex','-1'); // Adding tabindex for elements not focusable
                        $target.focus(); // Set focus again
                    };
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

});


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
      }  else if (w > 768) {
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
    $(window).smartresize(isotope);
  
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
  
  
  
    /*------------------------------- Element Appear Effect -----------------------------------------*/
    $('.from-top.delay-normal').each(function () {
      $(this).appear(function() {
        $(this).delay(150).animate({opacity:1,top:"0px"},600);
      }); 
    });
  
    $('.from-bottom.delay-normal').each(function () {
      $(this).appear(function() {
        $(this).delay(150).animate({opacity:1,bottom:"0px"},600);
      }); 
    });
  
  
    $('.from-bottom.delay-200').each(function () {
      $(this).appear(function() {
        $(this).delay(200).animate({opacity:1,bottom:"0px"},600);
      }); 
    });
  
    $('.from-bottom.delay-600').each(function () {
      $(this).appear(function() {
        $(this).delay(600).animate({opacity:1,bottom:"0px"},600);
      }); 
    });
  
    $('.from-bottom.delay-1000').each(function () {
      $(this).appear(function() {
        $(this).delay(1000).animate({opacity:1,bottom:"0px"},600);
      }); 
    });
  
    $('.from-bottom.delay-1400').each(function () {
      $(this).appear(function() {
        $(this).delay(1400).animate({opacity:1,bottom:"0px"},600);
      }); 
    });
  
    $('.from-left.delay-normal').each(function () {
      $(this).appear(function() {
        $(this).delay(150).animate({opacity:1,left:"0px"},600);
      }); 
    });
  
  
    $('.from-right.delay-normal').each(function () {
      $(this).appear(function() {
        $(this).delay(150).animate({opacity:1,right:"0px"},600);
      }); 
    });
  
    $('.from-right.delay-200').each(function () {
      $(this).appear(function() {
        $(this).delay(200).animate({opacity:1,right:"0px"},600);
      }); 
    });
  
    $('.from-right.delay-600').each(function () {
      $(this).appear(function() {
        $(this).delay(600).animate({opacity:1,right:"0px"},600);
      }); 
    });
  
    $('.from-right.delay-1000').each(function () {
      $(this).appear(function() {
        $(this).delay(1000).animate({opacity:1,right:"0px"},600);
      }); 
    });
  
    $('.from-right.delay-1400').each(function () {
      $(this).appear(function() {
        $(this).delay(1400).animate({opacity:1,right:"0px"},600);
      }); 
    });
  
    $('.fade-in.delay-normal').each(function () {
      $(this).appear(function() {
        $(this).delay(150).animate({opacity:1,right:"0px"},600);
      }); 
    });
  
});



// Making Array of all Images in Gallery
var items = [];
var images = $('img[data-rel="photoSwipe"]').each(function(index, img){
    var object = {
        src: img.src,
        w: img.naturalWidth,
        h: img.naturalHeight
    }
    items.push(object);
});
// Modifying href for each image
Object.entries(images).forEach(([key, img]) => {
    if(images.hasOwnProperty(key)){
        $(img).siblings('.stretched-link').attr('href', 'javascript:pswpInit(' + key + ')');
    }
})


// INITIALIZE PHOTOSWIPE

var pswpInit = function(startsAtIndex){

    if (!startsAtIndex) startsAtIndex = 0;

    var pswpElement = document.querySelectorAll('.pswp')[0];

    // build items array
    // var items = [
    //     {
    //         src: 'https://farm2.staticflickr.com/1043/5186867718_06b2e9e551_b.jpg',
    //         w: 964,
    //         h: 1024
    //     },
    //     {
    //         src: 'https://farm7.staticflickr.com/6175/6176698785_7dee72237e_b.jpg',
    //         w: 1024,
    //         h: 683
    //     },
    //     {
    //         src: 'https://placekitten.com/600/400',
    //         w: 600,
    //         h: 400
    //     },
    //     {
    //         src: 'https://placekitten.com/1200/900',
    //         w: 1200,
    //         h: 900
    //     }
    // ];

    // define options (if needed)
    var options = {
        // optionName: 'option value'
        // for example:
        index: startsAtIndex
    };

    // Initializes and opens PhotoSwipe
    var gallery = new PhotoSwipe( pswpElement, PhotoSwipeUI_Default, items, options);
    gallery.init();

}