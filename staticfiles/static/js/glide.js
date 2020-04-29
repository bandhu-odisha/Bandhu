var glide = new Glide('.glide',{
    type: 'carousel',
    focusAt: 'center',
    perView: 3,
    autoplay: 2000,
    gap: 30,
    breakpoints: {
        760:{
            perView: 1,

        }
    }
})

glide.mount()