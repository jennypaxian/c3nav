// Demo worker for animation canvas with framesource
let canvas, ctx, frame;

// Listen for the canvas from c3nav main thread
self.onmessage = (e) => {
    // Set it all up
    if (e.data.canvas !== undefined) {
        canvas = e.data.canvas;
        ctx = canvas.getContext("2d");
        setup();
    }

    // Pause logic, frame keeps reference
    if (e.data.pause)
        cancelAnimationFrame(frame);
    else if (e.data.image) {
        // We have received an image to be used as a pattern
        drawImagePattern(e.data.image);
        e.data.image.close();
    } else {
        frame = requestAnimationFrame(draw);
    }
};

// Text, Coords and Initial Direction (0 or 1)
var text = "C3NAV";
var x = 0;
var y = 43;
var dir = 1;

var width;
var patternCanvas;
var pctx;

function setup() {
    // Which font to use
    ctx.font = "32px Inter, sans-serif";
    width = ctx.measureText(text).width;

    postMessage({ framesource: 'header_logo_anim/badapple.mp4' });
}

function draw(t) {
    // Yeet everyting
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    x += dir;

    // Reverse direction when end reached
    if (x > canvas.width - width || x < 0) {
        dir *= -1;
    }

    // Render text at pos
    ctx.fillText(text, x, y);

    // Do it again
    frame = requestAnimationFrame(draw);
}

function drawImagePattern(image) {
    const w = image.displayWidth;
    const h = image.displayHeight;

    // Create pattern source canvas if not created yet
    if (!patternCanvas) {
        patternCanvas = new OffscreenCanvas(w, h);
        pctx = patternCanvas.getContext("2d");
    }

    // Use image as pattern
    pctx.drawImage(image, 0, 0, canvas.width, canvas.height);

    // Create pattern from canvas
    ctx.fillStyle = ctx.createPattern(patternCanvas, "repeat");
}