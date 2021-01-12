title_dict = {
            'Bachelor&Master': r"(B|M)(achelor|aster)?\.?\s?(of)?\s?(Sc|En)\w*\.?",  # Science and Engineering degrees
            'PhD': r"[Pp]h\.?\s?[Dd]\.?",
            'Postdoctoral&Fellow': r"([A-Z][^\s,.]+\w+\s?)*([Pp]ost[-]?doc|[Ff]ellow)\w*([A-Z][^\s,.()]+\w+\s?)*",
            'Lecturer': r"([Ss]enior)?\s?[Ll]ecturer",
            'Professor': r"([Aa]ssistant|[Aa]ssociate|[Aa]djunct|[Aa]/)?\s?[Pp]rof(?!(ession))\.?\w*"
        }
uni = r"([A-Z][^\s,.]+\w+\s?)*(Laboratory|[Ii]nstitute|[Uu]niversity|[Ff]acility|[Hh]ospital)(?!\s[a-eg-np-z])\s?(of\s|for\s)?(the\s)?([A-Z][^\s,.()<]+\w+\s?)*"
year = r"(\d{2}\/)?(19|20)\d{2}([^)]\W*)?(\d{2}\/)?(\d{2,4})?"  # matches number patterns such as: "2018", "2001-03", "03/2014~06/2017"
http_link = r'(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([/\w \.\?\:\-\=&;+#]*)'
href_link = r'(data-)?(href=\\?"[^>]*>)'
html_tag = r'</?(p|li|br)[\sA-Za-z\d=\"-:]*>'
end_of_sentence = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<![BMD]\.)(?<=\.)\s'   # split by the full stop at the end of each sentence (prevent grepping B./M./D.)
