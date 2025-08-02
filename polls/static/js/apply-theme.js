function hexToHSL(H) {
    let r = parseInt(H.slice(1, 3), 16) / 255;
    let g = parseInt(H.slice(3, 5), 16) / 255;
    let b = parseInt(H.slice(5, 7), 16) / 255;

    let cmin = Math.min(r, g, b),
        cmax = Math.max(r, g, b),
        delta = cmax - cmin;
    
    let h = 0, s = 0, l = 0;
    
    if (delta === 0) h = 0;
    else if (cmax === r) h = ((g - b) / delta) % 6;
    else if (cmax === g) h = (b - r) / delta + 2;
    else h = (r - g) / delta + 4;

    h = Math.round(h * 60);
    if (h < 0) h += 360;

    l = (cmax + cmin) / 2;
    s = delta === 0 ? 0 : delta / (1 - Math.abs(2 * l - 1));

    return {
        h: Math.round(h),
        s: Math.round(s * 100),
        l: Math.round(l * 100)
    };
}

fetch('/static/setting.json') // atau URL Django yang serve JSON
  .then(response => response.json())
  .then(data => {
    const root = document.documentElement;
    const { h, s, l } = hexToHSL(data.theme);
    root.style.setProperty('--clr-main-h', h);
    root.style.setProperty('--clr-main-s', `${s}%`);
    root.style.setProperty('--clr-main-l', `${l}%`);
    document.title = data.title;
  })
  .catch(err => console.error('Gagal load theme:', err));
