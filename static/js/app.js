// noinspection JSUnresolvedVariable

const imgDisplay = document.querySelector('.img-display')
const img = document.querySelector('.input-img')
const div1 = document.getElementById('mouse')
const div2 = document.getElementById('mouse2')
const selection = document.getElementById('selection')
const bitStart = document.getElementById('bit-start')
const bitEnd = document.getElementById('bit-end')
const timeStart = document.getElementById('time-start')
const timeEnd = document.getElementById('time-end')
const movingAverage = document.querySelector('input[name="moving_average"]')
const popup = document.getElementById('popup')
const popupBit = popup.querySelector('#popup-bit')
const popupTime = popup.querySelector('#popup-time')
const form = document.forms.main

let selecting = false
let current_time, current_bit

function inside_elem(event, elem) {
    const rect = elem.getBoundingClientRect()
    if (event.x < rect.left || event.x > rect.right) return false
    if (event.y < rect.top || event.y > rect.bottom) return false
    return true
}

function offset_with_elem(event, elem) {
    const rect = elem.getBoundingClientRect()
    return {
        x: (event.x - rect.x + elem.scrollLeft),
        y: (event.y - rect.y + elem.scrollTop)
    }
}

function get_pixel_pos(event) {
    const offset = offset_with_elem(event, imgDisplay)
    return {
        x: Math.min(offset.x - (offset.x % pixelScale), ((timeRange - 1) * pixelScale)),
        y: Math.min(offset.y - (offset.y % pixelScale), (bitRange) * pixelScale)
    }
}

function set_pixel_pos(event, elem, offsetX = 0, offsetY = 0) {
    const pos = get_pixel_pos(event)
    elem.style.marginLeft = `${pos.x + offsetX}px`
    elem.style.marginTop = `${pos.y + offsetY}px`
}

function parse_time(time) {
    let roundedMillis = time.getMilliseconds()
    if (time.getMilliseconds() % 250) {
        roundedMillis = (time.getMilliseconds() + 250 - time.getMilliseconds() % 250) % 1000
    }
    roundedMillis = Math.ceil(roundedMillis / 100) * 100
    return (`${time.toString('u')}.${String(roundedMillis)[0]}`).replace('Z', '')
}

document.onclick = function (e) {
    if (inside_elem(e, img)) {
        if (!selecting) {
            set_pixel_pos(e, div1)
            set_pixel_pos(e, div2)
            show_selection()

            bitStart.innerText = form.bit_start.value = String(current_bit)
            timeStart.innerText = form.time_start.value = parse_time(current_time)
            bitEnd.innerText = form.bit_end.value = ''
            timeEnd.innerText = form.time_end.value = ''
        } else {
            bitEnd.innerText = form.bit_end.value = String(current_bit)
            timeEnd.innerText = form.time_end.value = parse_time(current_time)
        }
        selecting = !selecting
    }
}
// TODO rely on mouse move
document.onmousemove = function (e) {
    if (selecting) {
        set_pixel_pos(e, div2)
        show_selection()
    }

    if (inside_elem(e, img)) {
        popup.style.display = 'block'
        const offset = offset_with_elem(e, imgDisplay)
        current_time = new Date(time_start)
        current_time.addSeconds(Math.trunc(offset.x / pixelScale) / pixelsPerSecond)
        current_bit = Math.trunc(offset.y / pixelScale) + bit_start

        popupTime.textContent = parse_time(current_time).split(' ')[1]
        popupBit.textContent = `${current_bit}`
        set_pixel_pos(e, popup, 10, 10)
    } else {
        popup.style.display = 'none'
    }
}


const imgOverlay = document.getElementById('overlay-img')
imgDisplay.onscroll = function () {
    imgOverlay.style.marginLeft = '-' + this.scrollLeft + 'px'
}


function show_selection() {
    const compareFunc = (a, b) => a - b
    const [top1, top2] = [parseInt(div1.style.marginTop), parseInt(div2.style.marginTop)].sort(compareFunc);
    const [left1, left2] = [parseInt(div1.style.marginLeft), parseInt(div2.style.marginLeft)].sort(compareFunc);
    selection.style.marginTop = `${top1}px`
    selection.style.marginLeft = `${left1}px`
    selection.style.height = `${top2 - top1 + pixelScale}px`
    selection.style.width = `${left2 - left1 + pixelScale}px`
}

function add_time_label() {
    const timeWrapper = document.querySelector('.label-time-wrapper')
    const imgWidth = img.width
    let html = ''
    let time = new Date(time_start)
    let totalWidth = 0

    if (imgWidth === 0) {
        setTimeout(add_time_label)
        return
    }

    let offset_width = 0
    if (time.getMilliseconds()) {
        const offset_millis = 1000 - time.getMilliseconds() % 1000;
        offset_width = offset_millis / 1000 * pixelsPerSecond * pixelScale
        time.addMilliseconds(offset_millis)
        totalWidth += offset_width
    }

    while (totalWidth < imgWidth) {
        const style = offset_width ? `style="margin-left: ${offset_width - 0.15 * pixelScale}px"` : ''
        offset_width = 0
        html += `<span class="label-time" ${style}>${parse_time(time).split(' ')[1].split('.')[0]}</span>`
        time.addSeconds(1)
        totalWidth += pixelsPerSecond * pixelScale
    }
    timeWrapper.innerHTML = html
}

function show_output_labels() {
    const form = document.forms.main
    bitStart.innerText = form.bit_start.value = String(bit_start)
    bitEnd.innerText = form.bit_end.value = String(bit_end)
    timeStart.innerText = form.time_start.value = parse_time(time_start)
    timeEnd.innerText = form.time_end.value = parse_time(time_end)
}