from fpdf import FPDF


class PDF(FPDF):

    title = None

    def set_title_name(self, title):
        self.title = title

    def get_title(self):
        return self.title

    def header(self):
        # TODO remove header from first page
        # font
        self.set_font('helvetica', 'B', 15)
        # Calculate width of title and position
        title_w = self.get_string_width(self.get_title()) + 6
        doc_w = self.w
        self.set_x((doc_w - title_w) / 2)
        # colors of frame, background, and text

        self.set_draw_color(0, 0, 0)
        self.set_fill_color(255, 255, 255)
        self.set_text_color(0, 0, 0)
        # Thickness of frame (border)
        self.set_line_width(0.5)
        # Title
        self.cell(title_w, 10, self.get_title(), border=1, ln=1, align='C', fill=1)
        # line break
        self.ln(10)

    # page footer
    def footer(self):
        if not self.page_no() == 1 :
            # Set position of the footer
            self.set_y(-15)
            # set font
            self.set_font('helvetica', 'I', 10)
            # page number
            self.cell(0, 10, f'Page {self.page_no()}/nb', align = 'C')

    # Adding scan title to start of each scan
    def scan_title(self, scan_num, scan_title, link):
        # Set link location
        self.set_link(link)
        # set font
        self.set_font('helvetica', '', 12)
        # set font color
        self.set_text_color(255, 255, 255)
        # background color
        self.set_fill_color(110, 0, 150)
        # scan title
        scan_title = f'Scan {scan_num} : {scan_title}'
        self.cell(0, 5, scan_title, ln=1, fill=1)
        # change font color back to black
        self.set_text_color(0, 0, 0)
        # line break
        self.ln()

    # scan content
    def scan_body(self, name, scan_title):
        # read text file
        with open(name, 'rb') as fh:
            txt = fh.read().decode('latin-1')
        # set font
        self.set_font('times', '', 12)
        # insert text
        self.multi_cell(0, 5, txt)
        # line break
        self.ln()
        # end each scan
        self.set_font('times', 'I', 12)
        self.cell(0, 5, f'END OF {scan_title}')

    def print_scan(self, scan_num, scan_title, name, link):
        self.add_page()
        self.scan_title(scan_num, scan_title, link)
        self.scan_body(name, scan_title)