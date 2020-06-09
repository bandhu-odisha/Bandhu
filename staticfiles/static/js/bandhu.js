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
