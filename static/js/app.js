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
const popup = document.getElementById('popup')
const popupBit = popup.querySelector('#popup-bit')
const popupTime = popup.querySelector('#popup-time')
const timeWrapper = document.querySelector('.label-time-wrapper')
const form = document.forms.main

let selecting = false
let current_time, current_bit
let current_x, current_y
let selected = {
    x: {
        start: -1,
        end: -1
    },
    y: {
        start: -1,
        end: -1
    },
}

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
    return `${time.toString('u')}.${Math.trunc(time.getMilliseconds() / 100)}`.replace('Z', '')
}

document.onclick = function (e) {
    if (inside_elem(e, img)) {
        if (!selecting) {
            set_pixel_pos(e, div1)
            set_pixel_pos(e, div2)
            selected.x.start = current_x
            selected.y.start = current_y
            show_selection()

            bitStart.innerText = form.bit_start.value = current_bit
            timeStart.innerText = form.time_start.value = parse_time(current_time)
            bitEnd.innerText = form.bit_end.value = ''
            timeEnd.innerText = form.time_end.value = ''
        } else {
            [selected.x.start, selected.x.end] = [selected.x.start, current_x].sort();
            [selected.y.start, selected.y.end] = [selected.y.start, current_y].sort();

            const bit = {
                start: selected.x.start + bit_start,
                end: selected.x.end + bit_end
            }
            const time = {
                start: `${parse_time(time_start).split(' ')[0]} ${time_map[selected.y.start][selected.x.start]}`,
                end: `${parse_time(time_start).split(' ')[0]} ${time_map[selected.y.end][selected.x.end]}`,
            }

            bitStart.innerText = form.bit_start.value = bit.start
            timeStart.innerText = form.time_start.value = time.start
            bitEnd.innerText = form.bit_end.value = bit.end
            timeEnd.innerText = form.time_end.value = time.end
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
        current_bit = Math.min(Math.trunc(offset.y / pixelScale) + bit_start, bit_end)
        const time_str = time_map[current_bit][Math.trunc(offset.x / pixelScale)]
        current_time = new Date(`${parse_time(time_start).split(' ')[0]} ${time_str}`)

        current_y = Math.min(Math.trunc(offset.y / pixelScale), bit_end - bit_start + 1)
        current_x = Math.trunc(offset.x / pixelScale)

        popupTime.textContent = time_str
        popupBit.textContent = current_bit
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


function add_time_label(labels, labels_pos) {
    let html = ''
    let previous = 0

    for (let ind = 0; ind < labels.length; ind++) {
        const margin_left = Math.max(0, labels_pos[ind] - previous - 1) * pixelScale
        const style = `style="margin-left: ${margin_left}px"`
        html += `<span class="label-time" ${style}">${labels[ind]}</span>`

        previous = labels_pos[ind]
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