from .models import Player, Injury
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
import io
from reportlab.lib.colors import HexColor

def wrap_text(text, width, canvas, font_name, font_size):
    """
    Wraps text so it fits within a specific width when using the specified font name and size.
    This function breaks the text into lines that fit within the specified width.
    """
    canvas.setFont(font_name, font_size)
    wrapped_lines = []
    words = text.split()
    while words:
        line = ''
        while words and canvas.stringWidth(line + words[0], font_name, font_size) < width:
            line += (words.pop(0) + ' ')
        wrapped_lines.append(line)
    return wrapped_lines

def generate_pdf(player_id,risk,info):
    buf = io.BytesIO()

    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    
    width, height = letter  # Unpack the width and height of the page
    textob = c.beginText()
    textob.moveCursor(0, 0)

    header_color = HexColor("#469285")  # Example: a yellow color
    header_x = inch / 2 -50  # Example starting x position
    header_y = textob.getY() - 15  # Get current y position from text object and adjust
    header_width = width + 50 # Full width of the page minus margins
    header_height = 75  # Example height of the banner

    c.setFillColor(header_color)
    c.rect(header_x, header_y, header_width, header_height, fill=1, stroke=0)

    # Adjust text color if needed
    c.setFillColorRGB(0, 0, 0)  # Black for text

    # Position and draw the "Risk Assessment" title over the rectangle
    textob.setFont("Helvetica-Bold", 14)
    textob.setTextOrigin(header_x, header_y)  # Adjust text position to fit within the banner
    textob.textOut("The Football Physician")  # Using textOut to stay on the same line

    # Draw the risk level next to the "Risk Assessment" text
    textob.setFont("Helvetica", 14)
    #textob.textOut(" " + risk)  # Space as a separator

    image_path = 'C:/Users/Omar/Documents/FYP/fyp/website/FP-logo-removebg.jpg' 

    # Display an image (e.g., player's photo)
    # You can adjust the position and size as needed
    image_width = 2 * inch  # Example width of the image
    image_height = 2 * inch  # Example height of the image
    image_x = width - image_width - inch + 50 # Subtracting the image width and a margin
    image_y = inch   # Margin from the top
    c.drawImage(image_path, image_x, image_y, width=image_width, height=image_height)


    # Assuming you want to place the image at the top right

    textob = c.beginText()
    #textob.setTextOrigin(inch,inch)
    textob.setFont("Helvetica",14)
    textob.setFillColorRGB(0, 0, 0)  # Red


    player = Player.objects.filter(id=player_id).first()
    filename = f'{player.first_name}_{player.last_name}_Report.pdf'

    # Calculate center for the player name
    name = f'{player.first_name} {player.last_name}' + "  ACL Risk Report"
    text_width = c.stringWidth(name, "Helvetica-Bold", 18)  # Measure text width with desired font and size
    text_x_center = (width - text_width) / 2  # Calculate x position to center text
    

    # Display player name larger and at the top middle of the page
    textob.setFont("Helvetica-Bold", 18)  # Set font size larger for the name
    textob.setTextOrigin(text_x_center, inch+25)  # Set origin to center name
    textob.textLine(name)
    textob.setFont("Helvetica", 14)  # Reset font size for the rest

    # Move down after the name
    textob.moveCursor(-160, 20)


    headings = ["Position:         ", "Date of Birth: ", "Height (cm):   ", "Weight (kg):    ", "Nationality:     "]
    values = [
        player.position,
        str(player.date_of_birth),
        str(player.height) + " cm",
        str(player.weight) + " kg",
        player.country
    ]

    for heading, value in zip(headings, values):
        # Draw heading in bold
        textob.setFont("Helvetica-Bold", 14)
        textob.textOut(heading + " ")
        
        # Draw value in regular font
        textob.setFont("Helvetica", 14)
        textob.textLine(value)


     # Display the risk in PDF
    textob.moveCursor(200, 30)

    if risk == "Extreme Risk":
        risk_banner_color = HexColor("#FF0000") 
    elif risk == "Very High Risk":
        risk_banner_color = HexColor("#FF4500") 
    elif risk == "High Risk":
        risk_banner_color = HexColor("#FFA500") 
    elif risk == "Moderate Risk":
        risk_banner_color = HexColor("#FFD700") 
    elif risk == "Low Risk":
        risk_banner_color = HexColor("#90EE90") 
    elif risk == "Very Low Risk":
        risk_banner_color = HexColor("#00FF00") 
    banner_x = inch / 2  # Example starting x position
    banner_y = textob.getY() - 15  # Get current y position from text object and adjust
    banner_width = width - inch # Full width of the page minus margins
    banner_height = 30  # Example height of the banner

    c.setFillColor(risk_banner_color)
    c.rect(banner_x, banner_y, banner_width, banner_height, fill=1, stroke=0)

    # Adjust text color if needed
    c.setFillColorRGB(0, 0, 0)  # Black for text

    # Position and draw the "Risk Assessment" title over the rectangle
    textob.setFont("Helvetica-Bold", 14)
    textob.setTextOrigin(banner_x + 150, banner_y + 20)  # Adjust text position to fit within the banner
    textob.textOut("Risk Assessment:")  # Using textOut to stay on the same line

    # Draw the risk level next to the "Risk Assessment" text
    textob.setFont("Helvetica", 14)
    textob.textOut(" " + risk)  # Space as a separator

    textob.moveCursor(-165, 50)

    # #Display injuries in PDF
    injuries = Injury.objects.filter(player=player_id).order_by('injury_start_date')
    
    # Headers for the table
    headers = ["Injury", "Start Date", "End Date", "Age at Injury"]
    # Assuming 'injuries' is your queryset or list of injury objects
    injury_data = []
    for injury in injuries: 
        injury_data.append([injury.injury, str(injury.injury_start_date), str(injury.injury_end_date) if injury.injury_end_date else str(date.today()), 
        str(injury.injury_age)] )
        
        
    table_data = injury_data + [headers]

    # Set starting positions
    start_x = 75
    start_y = 420
    row_height = 20
    col_widths = [150, 100, 100, 100]  # Adjust the widths as needed

    def draw_table(canvas, data, start_x, start_y, row_height, col_widths):
        num_rows = len(data)
        num_cols = len(data[0])

        # Draw the grid
        for row in range(num_rows + 1):
            for col in range(num_cols + 1):
                # Vertical lines
                if row == 0:
                    x = start_x + sum(col_widths[:col])
                    canvas.line(x, start_y, x, start_y - num_rows * row_height)
                # Horizontal lines
                y = start_y - row * row_height
                canvas.line(start_x, y, start_x + sum(col_widths), y)

        # Insert the text
        for row, row_data in enumerate(data):
            for col, cell in enumerate(row_data):
                text_x = start_x + sum(col_widths[:col]) + 5
                text_y = start_y - row * row_height - row_height / 2
                canvas.drawString(text_x, text_y, cell)

    # Use the function to draw the table
    draw_table(c, table_data, start_x, start_y, row_height, col_widths)


    textob.moveCursor(0, 130)

    
    #Display info(an array) in PDF
    info_titles= ["Exercises to avoid:","Exercises to do:","Advice:"]

    additional_info_lines = []
    max_width = width - 2 * inch
    for info_title,info_text in zip(info_titles,info):
        additional_info_lines.append(info_title)
        wrapped_lines = wrap_text(info_text, max_width, c, "Helvetica", 14)
        additional_info_lines.extend(wrapped_lines)
        additional_info_lines.append('')  # Add a blank line between sections for readability

    # Display the wrapped lines
    textob.setFont("Helvetica-Bold", 14)
    textob.textLine("")
    textob.textLine("Additional Information:")
    textob.setFont("Helvetica", 14)
    for line in additional_info_lines:
        textob.textLine(line)

    footer_color = HexColor("#469285")  # Example: a yellow color
    footer_x = 0  # Example starting x position
    footer_y = height - 50  # Get current y position from text object and adjust
    footer_width = width + 50 # Full width of the page minus margins
    footer_height = 75  # Example height of the banner

    c.setFillColor(footer_color)
    c.rect(footer_x, footer_y, footer_width, footer_height, fill=1, stroke=0)

    # Adjust text color if needed
    #c.setFillColorRGB(255, 255, 255)  # Black for text

    # Position and draw the "Risk Assessment" title over the rectangle
    

    c.setTitle(f'{player.first_name} {player.last_name} Report')
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    return buf,filename