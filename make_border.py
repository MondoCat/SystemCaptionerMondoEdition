from PIL import Image, ImageDraw

def create_cooler_border():
    width = 400
    height = 540
    
    img = Image.new('RGBA', (width, height), color='#2e2e2e')
    draw = ImageDraw.Draw(img, 'RGBA')
    
    for y in range(0, height, 4):
        draw.line([(0, y), (width, y)], fill='#242424', width=2)
        
    draw.rectangle([0, 0, width-1, height-1], outline=(0, 255, 255, 80), width=6)
    draw.rectangle([1, 1, width-2, height-2], outline=(0, 255, 255, 150), width=4)
    draw.rectangle([2, 2, width-3, height-3], outline=(0, 255, 255, 255), width=2)
    
    draw.rectangle([10, 10, width-11, height-11], outline=(255, 0, 255, 80), width=5)
    draw.rectangle([11, 11, width-12, height-12], outline=(255, 0, 255, 180), width=3)
    draw.rectangle([12, 12, width-13, height-13], outline=(255, 0, 255, 255), width=1)
    
    corner_len = 35
    thick = 5
    c_color = '#39ff14' 
    
    draw.rectangle([0, 0, corner_len, thick-1], fill=c_color)
    draw.rectangle([0, 0, thick-1, corner_len], fill=c_color)
    
    draw.rectangle([width-corner_len, 0, width, thick-1], fill=c_color)
    draw.rectangle([width-thick, 0, width, corner_len], fill=c_color)
    
    draw.rectangle([0, height-thick, corner_len, height], fill=c_color)
    draw.rectangle([0, height-corner_len, thick-1, height], fill=c_color)
    
    draw.rectangle([width-corner_len, height-thick, width, height], fill=c_color)
    draw.rectangle([width-thick, height-corner_len, width, height], fill=c_color)

    img.save('border.png')
    print("Coolerborder.png generated successfully!")

if __name__ == "__main__":
    create_cooler_border()