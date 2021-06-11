const loadingIcon = document.querySelector('.loading')
let time_start, time_end

function check_image() {
    $.getJSON(`/get-image?img_url=${img_url}`, load_image)
}


function load_image(data) {
    if (!data.url) {
        setTimeout(check_image, 1000)
        return
    }
    const inputImg = document.querySelector('.input-img')
    inputImg.src = data.url
    inputImg.style.width = `${data.width * pixelScale}px`
    inputImg.style.height = `${data.height * pixelScale}px`
    timeRange = data.width
    time_start = eval(data.start)
    time_end = eval(data.end)
    add_time_label()
    show_output_labels()
    loadingIcon.classList.toggle('invisible')
}


(() => {
    check_image()
    document.getElementById('submit-btn').onclick = upload_files
})()


function upload_files() {
    const data = new FormData($('form[name="files"]')[0])
    console.log(data)
    if (!data.get('csv') && !data.get('weight')) return go_to_next_page()

    $.ajax({
        // Your server script to process the upload
        url: '/upload',
        type: 'POST',

        // Form data
        data: data,

        // Tell jQuery not to process data or worry about content-type
        // You *must* include these options!
        cache: false,
        contentType: false,
        processData: false,

        // Custom XMLHttpRequest
        xhr: function () {
            let myXhr = $.ajaxSettings.xhr();
            if (myXhr.upload) {
                // For handling the progress of the upload
                myXhr.upload.addEventListener('progress', function (e) {
                    if (e.lengthComputable) {
                        console.log(`${e.loaded}/${e.total}`)
                    }
                }, false);
                myXhr.upload.addEventListener('load', go_to_next_page)
            }
            return myXhr;
        }
    });
}


function go_to_next_page() {
    $('form[name="main"]').submit()
}