// // Making Array of all Images in Gallery
// var items = [];
// var images = $('img[data-rel="photoSwipe"]').each(function(index, img){
//     var object = {
//         src: img.src,
//         w: img.naturalWidth,
//         h: img.naturalHeight
//     }
//     items.push(object);
// });
// // Modifying href for each image
// Object.entries(images).forEach(([key, img]) => {
//     if(images.hasOwnProperty(key)){
//         $(img).siblings('.stretched-link').attr('href', 'javascript:pswpInit(' + key + ')');
//     }
// })


// // INITIALIZE PHOTOSWIPE

// var pswpInit = function(startsAtIndex){

//     if (!startsAtIndex) startsAtIndex = 0;

//     var pswpElement = document.querySelectorAll('.pswp')[0];

//     // build items array
//     // var items = [
//     //     {
//     //         src: 'https://farm2.staticflickr.com/1043/5186867718_06b2e9e551_b.jpg',
//     //         w: 964,
//     //         h: 1024
//     //     },
//     //     {
//     //         src: 'https://farm7.staticflickr.com/6175/6176698785_7dee72237e_b.jpg',
//     //         w: 1024,
//     //         h: 683
//     //     },
//     //     {
//     //         src: 'https://placekitten.com/600/400',
//     //         w: 600,
//     //         h: 400
//     //     },
//     //     {
//     //         src: 'https://placekitten.com/1200/900',
//     //         w: 1200,
//     //         h: 900
//     //     }
//     // ];

//     // define options (if needed)
//     var options = {
//         // optionName: 'option value'
//         // for example:
//         index: startsAtIndex
//     };

//     // Initializes and opens PhotoSwipe
//     var gallery = new PhotoSwipe( pswpElement, PhotoSwipeUI_Default, items, options);
//     gallery.init();

// }


// HEADER TEXT ANIMATION
$(function () {
    var $header = $("#header-text");
    var header = ['<span class="d-block" lang="or" style="font-family: oriya;">ସବାଶେଷ  ମଣିଷର</span>', '<span class="d-block" style="font-weight:normal; font-family:cursive; text-transform: capitalize;">The Friend of the Last Man</span>'];
    var position = -1;
    
    !function loop() {
        position = (position + 1) % header.length;
        $header.html(header[position])
        .fadeIn(1000)
        .delay(4000)
        .fadeOut(1000, loop);
    }();
});

// Recent Activities Collapsible
$(document).ready(function() {
    if ($(window).scrollTop() <= 200) $('#collapseExample').collapse('show')
    $(window).scroll(function() {
        if ($(this).scrollTop() > 200) {
            $('#collapseExample').collapse('hide')
        } 
        else {
            $('#collapseExample').collapse('show')
        }
    }); 
});