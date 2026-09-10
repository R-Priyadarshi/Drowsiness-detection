import re

with open("templates/index.html", "r") as f:
    content = f.read()

# Add crossorigin
content = content.replace('<img src="" data-src="{{ url_for(\'video_feed\') }}" alt="Camera Feed" id="video-feed">', 
                          '<img src="" data-src="{{ url_for(\'video_feed\') }}" alt="Camera Feed" id="video-feed" crossorigin="anonymous">')

# Wrap pixel reading in try-catch
old_pixel_js = """            hoverCtx.drawImage(videoFeed, 0, 0, hoverCanvas.width, hoverCanvas.height);
            // Read exactly 1 pixel
            const pixel = hoverCtx.getImageData(x, y, 1, 1).data;
            
            pixelInfo.innerHTML = `
                <span>(x=${x.toString().padStart(3, ' ')}, y=${y.toString().padStart(3, ' ')})</span>
                <span>~</span>
                <span><span style="color: #ff4444">R:${pixel[0].toString().padStart(3, ' ')}</span> <span style="color: #44ff44">G:${pixel[1].toString().padStart(3, ' ')}</span> <span style="color: #4488ff">B:${pixel[2].toString().padStart(3, ' ')}</span></span>
            `;"""

new_pixel_js = """            try {
                hoverCtx.drawImage(videoFeed, 0, 0, hoverCanvas.width, hoverCanvas.height);
                const pixel = hoverCtx.getImageData(x, y, 1, 1).data;
                
                pixelInfo.innerHTML = `
                    <span>(x=${x.toString().padStart(3, ' ')}, y=${y.toString().padStart(3, ' ')})</span>
                    <span>~</span>
                    <span><span style="color: #ff4444">R:${pixel[0].toString().padStart(3, ' ')}</span> <span style="color: #44ff44">G:${pixel[1].toString().padStart(3, ' ')}</span> <span style="color: #4488ff">B:${pixel[2].toString().padStart(3, ' ')}</span></span>
                `;
            } catch (err) {
                pixelInfo.innerHTML = `
                    <span>(x=${x.toString().padStart(3, ' ')}, y=${y.toString().padStart(3, ' ')})</span>
                    <span>~</span>
                    <span style="color: #999;">R:--- G:--- B:--- (CORS block)</span>
                `;
            }"""
content = content.replace(old_pixel_js, new_pixel_js)

with open("templates/index.html", "w") as f:
    f.write(content)

