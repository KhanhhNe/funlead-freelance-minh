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

let selecting = false;

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

function compute_output() {
    let {top, left, bottom, right} = selection.getBoundingClientRect()
    const displayRect = imgDisplay.getBoundingClientRect()
    left += imgDisplay.scrollLeft - displayRect.x
    right += imgDisplay.scrollLeft - displayRect.x
    top += imgDisplay.scrollTop - displayRect.y
    bottom += imgDisplay.scrollTop - displayRect.y

    let bit = {
        start: bit_start + Math.trunc(top / pixelScale),
        end: bit_start + Math.trunc(bottom / pixelScale - 1)
    }
    let time = {
        start: (new Date(time_start)).addMilliseconds(left / pixelScale / pixelsPerSecond * 1000),
        end: (new Date(time_start)).addMilliseconds((right / pixelScale - 1) / pixelsPerSecond * 1000)
    }
    const form = document.forms.main
    bitStart.innerText = form.bit_start.value = String(bit.start)
    bitEnd.innerText = form.bit_end.value = String(bit.end)
    timeStart.innerText = form.time_start.value = parse_time(time.start)
    timeEnd.innerText = form.time_end.value = parse_time(time.end)
}

document.onclick = function (e) {
    if (inside_elem(e, img)) {
        if (!selecting) {
            set_pixel_pos(e, div1)
            selection.style.width = '0px'
        } else {
            set_pixel_pos(e, div2)
            show_selection()
            compute_output()
        }
        selecting = !selecting
    }
}

document.onmousemove = function (e) {
    if (selecting) {
        set_pixel_pos(e, div2)
        show_selection()
    }

    if (inside_elem(e, img)) {
        popup.style.display = 'block'
        const offset = offset_with_elem(e, imgDisplay)
        const time = new Date(time_start)
        time.addSeconds(Math.trunc(offset.x / pixelScale) / pixelsPerSecond)
        popupTime.textContent = parse_time(time).split(' ')[1]
        popupBit.textContent = `${Math.trunc(offset.y / pixelScale) + bit_start}`
        set_pixel_pos(e, popup, 10, 10)
    } else {
        popup.style.display = 'none'
    }
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
    time.addMilliseconds(250)
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
        time.addSeconds(2)
        totalWidth += pixelsPerSecond * 2 * pixelScale
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