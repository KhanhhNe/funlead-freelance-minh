const loadingIcon = document.querySelector('.loading')
let time_start, time_end, time_map

function check_image() {
    $.getJSON(`/get-image?img_url=${img_url}`, load_image)
}


function load_image(data) {
    loadingIcon.classList.remove('invisible')

    if (data.success === false) {
        loadingIcon.classList.add('invisible')
        alert(`There was an error processing:\n${data.message}`)
        return
    }

    if (!data.url) {
        setTimeout(check_image, 1000)
        return
    }

    const inputImg = document.querySelector('.input-img')
    inputImg.src = data.url
    timeWrapper.style.width = inputImg.style.width = `${data.width * pixelScale}px`
    inputImg.style.height = `${data.height * pixelScale}px`
    timeRange = data.width
    time_start = eval(data.start)
    time_end = eval(data.end)
    add_time_label(data.labels, data.labels_pos)
    time_map = data.time_map
    show_output_labels()

    loadingIcon.classList.add('invisible')
}


(() => {
    if (document.querySelector('.img-display')) {
        check_image()
    }
    document.getElementById('submit-btn').onclick = upload_files
    $('form[name="files"]').submit(function (e) {
        e.preventDefault()
    })
})()


function upload_files() {
    const data = new FormData($('form[name="files"]')[0])

    if (!data.get('csv').name && !data.get('weight').name) {
        go_to_next_page()
        return false
    }

    loadingIcon.classList.remove('invisible')
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
                myXhr.upload.addEventListener('load', () => setTimeout(function () {
                    if (data.get('csv').name) {
                        $('form[name="main"] input:not([name="moving_average"])').remove()
                    }
                    go_to_next_page()
                }, 1000))
            }
            return myXhr;
        }
    });
    return false;
}


function go_to_next_page() {
    loadingIcon.classList.add('invisible')
    $('form[name="main"]').submit()
}