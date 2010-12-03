#! /usr/bin/env python
# -*- coding: utf-8 -*-

#   math2html: convert LaTeX equations to HTML output.
#
#   Copyright (C) 2009,2010 Alex Fernández
#   Released  without warranties or conditions of any kind
#   under the terms of the Apache License, Version 2.0
#   http://www.apache.org/licenses/LICENSE-2.0

#   Based on eLyXer: convert LyX source files to HTML output.
#   http://elyxer.nongnu.org/

# --end--
# Alex 20101110
# eLyXer standalone formula conversion to HTML.




import sys

class Trace(object):
  "A tracing class"

  debugmode = False
  quietmode = False
  showlinesmode = False

  prefix = None

  def debug(cls, message):
    "Show a debug message"
    if not Trace.debugmode or Trace.quietmode:
      return
    Trace.show(message, sys.stdout)

  def message(cls, message):
    "Show a trace message"
    if Trace.quietmode:
      return
    if Trace.prefix and Trace.showlinesmode:
      message = Trace.prefix + message
    Trace.show(message, sys.stdout)

  def error(cls, message):
    "Show an error message"
    message = '* ' + message
    if Trace.prefix and Trace.showlinesmode:
      message = Trace.prefix + message
    Trace.show(message, sys.stderr)

  def fatal(cls, message):
    "Show an error message and terminate"
    Trace.error('FATAL: ' + message)
    exit(-1)

  def show(cls, message, channel):
    "Show a message out of a channel"
    message = message.encode('utf-8')
    channel.write(message + '\n')

  debug = classmethod(debug)
  message = classmethod(message)
  error = classmethod(error)
  fatal = classmethod(fatal)
  show = classmethod(show)












class Cloner(object):
  "An object used to clone other objects."

  def clone(cls, original):
    "Return an exact copy of an object."
    "The original object must have an empty constructor."
    return cls.create(original.__class__)

  def create(cls, type):
    "Create an object of a given class."
    clone = type.__new__(type)
    clone.__init__()
    return clone

  clone = classmethod(clone)
  create = classmethod(create)

class ContainerExtractor(object):
  "A class to extract certain containers."

  def __init__(self, config):
    "The config parameter is a map containing three lists: allowed, copied and extracted."
    "Each of the three is a list of class names for containers."
    "Allowed containers are included as is into the result."
    "Cloned containers are cloned and placed into the result."
    "Extracted containers are looked into."
    "All other containers are silently ignored."
    self.allowed = config['allowed']
    self.cloned = config['cloned']
    self.extracted = config['extracted']

  def extract(self, container):
    "Extract a group of selected containers from a container."
    list = []
    locate = lambda c: c.__class__.__name__ in self.allowed + self.cloned
    recursive = lambda c: c.__class__.__name__ in self.extracted
    process = lambda c: self.process(c, list)
    container.recursivesearch(locate, recursive, process)
    return list

  def process(self, container, list):
    "Add allowed containers, clone cloned containers and add the clone."
    name = container.__class__.__name__
    if name in self.allowed:
      list.append(container)
    elif name in self.cloned:
      list.append(self.safeclone(container))
    else:
      Trace.error('Unknown container class ' + name)

  def safeclone(self, container):
    "Return a new container with contents only in a safe list, recursively."
    clone = Cloner.clone(container)
    clone.output = container.output
    clone.contents = self.extract(container)
    return clone







import os.path
import sys


class BibStylesConfig(object):
  "Configuration class from config file"

  abbrvnat = {
      
      u'@article':u'$authors. $title. <i>$journal</i>,{ {$volume:}$pages,} $month $year.{ doi: $doi.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'cite':u'$surname($year)', 
      u'default':u'$authors. <i>$title</i>. $publisher, $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      }

  alpha = {
      
      u'@article':u'$authors. $title.{ <i>$journal</i>{, {$volume}{($number)}}{: $pages}{, $year}.}{ <a href="$url">$url</a>.}{ <a href="$filename">$filename</a>.}{ $note.}', 
      u'cite':u'$Sur$YY', 
      u'default':u'$authors. $title.{ <i>$journal</i>,} $year.{ <a href="$url">$url</a>.}{ <a href="$filename">$filename</a>.}{ $note.}', 
      }

  authordate2 = {
      
      u'@article':u'$authors. $year. $title. <i>$journal</i>, <b>$volume</b>($number), $pages.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@book':u'$authors. $year. <i>$title</i>. $publisher.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'cite':u'$surname, $year', 
      u'default':u'$authors. $year. <i>$title</i>. $publisher.{ URL <a href="$url">$url</a>.}{ $note.}', 
      }

  default = {
      
      u'@article':u'$authors: “$title”, <i>$journal</i>,{ pp. $pages,} $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@book':u'{$authors: }<i>$title</i>{ ($editor, ed.)}.{{ $publisher,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@booklet':u'$authors: <i>$title</i>.{{ $publisher,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@conference':u'$authors: “$title”, <i>$journal</i>,{ pp. $pages,} $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@inbook':u'$authors: <i>$title</i>.{{ $publisher,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@incollection':u'$authors: <i>$title</i>{ in <i>$booktitle</i>{ ($editor, ed.)}}.{{ $publisher,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@inproceedings':u'$authors: “$title”, <i>$journal</i>,{ pp. $pages,} $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@manual':u'$authors: <i>$title</i>.{{ $publisher,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@mastersthesis':u'$authors: <i>$title</i>.{{ $publisher,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@misc':u'$authors: <i>$title</i>.{{ $publisher,}{ $howpublished,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@phdthesis':u'$authors: <i>$title</i>.{{ $publisher,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@proceedings':u'$authors: “$title”, <i>$journal</i>,{ pp. $pages,} $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@techreport':u'$authors: <i>$title</i>, $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@unpublished':u'$authors: “$title”, <i>$journal</i>, $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'cite':u'$index', 
      u'default':u'$authors: <i>$title</i>.{{ $publisher,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      }

  defaulttags = {
      u'YY':u'??', u'authors':u'', u'surname':u'', 
      }

  ieeetr = {
      
      u'@article':u'$authors, “$title”, <i>$journal</i>, vol. $volume, no. $number, pp. $pages, $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@book':u'$authors, <i>$title</i>. $publisher, $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'cite':u'$index', 
      u'default':u'$authors, “$title”. $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      }

  plain = {
      
      u'@article':u'$authors. $title.{ <i>$journal</i>{, {$volume}{($number)}}{:$pages}{, $year}.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@book':u'$authors. <i>$title</i>. $publisher,{ $month} $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@incollection':u'$authors. $title.{ In <i>$booktitle</i> {($editor, ed.)}.} $publisher,{ $month} $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@inproceedings':u'$authors. $title. { <i>$booktitle</i>{, {$volume}{($number)}}{:$pages}{, $year}.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'cite':u'$index', 
      u'default':u'{$authors. }$title.{{ $publisher,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      }

  vancouver = {
      
      u'@article':u'$authors. $title. <i>$journal</i>, $year{;{<b>$volume</b>}{($number)}{:$pages}}.{ URL: <a href="$url">$url</a>.}{ $note.}', 
      u'@book':u'$authors. $title. {$publisher, }$year.{ URL: <a href="$url">$url</a>.}{ $note.}', 
      u'cite':u'$index', 
      u'default':u'$authors. $title; {$publisher, }$year.{ $howpublished.}{ URL: <a href="$url">$url</a>.}{ $note.}', 
      }

class BibTeXConfig(object):
  "Configuration class from config file"

  escaped = {
      u'\\"A':u'Ä', u'\\"E':u'Ë', u'\\"I':u'Ï', u'\\"O':u'Ö', u'\\"U':u'Ü', 
      u'\\"\\i':u'ï', u'\\"a':u'ä', u'\\"e':u'ë', u'\\"i':u'ï', u'\\"o':u'ö', 
      u'\\"u':u'ü', u'\\"y':u'ÿ', u'\\"{A}':u'Ä', u'\\"{E}':u'Ë', 
      u'\\"{I}':u'Ï', u'\\"{O}':u'Ö', u'\\"{U}':u'Ü', u'\\"{\\i}':u'ï', 
      u'\\#':u'#', u'\\$':u'$', u'\\%':u'%', u'\\&':u'&', u'\\\'A':u'Á', 
      u'\\\'E':u'É', u'\\\'I':u'Í', u'\\\'O':u'Ó', u'\\\'U':u'Ú', 
      u'\\\'Y':u'Ý', u'\\\'\\i':u'í', u'\\\'a':u'á', u'\\\'e':u'é', 
      u'\\\'i':u'í', u'\\\'o':u'ó', u'\\\'u':u'ú', u'\\\'y':u'ý', 
      u'\\\'{A}':u'Á', u'\\\'{E}':u'É', u'\\\'{I}':u'Í', u'\\\'{O}':u'Ó', 
      u'\\\'{U}':u'Ú', u'\\\'{Y}':u'Ý', u'\\\'{\\i}':u'í', u'\\\'{c}':u'ć', 
      u'\\,':u' ', u'\\;':u' ', u'\\AA':u'Å', u'\\AE':u'Æ', u'\\DH':u'Ð', 
      u'\\O':u'Ø', u'\\TH':u'Þ', u'\\^A':u'Â', u'\\^E':u'Ê', u'\\^I':u'Î', 
      u'\\^O':u'Ô', u'\\^U':u'Û', u'\\^\\i':u'î', u'\\^a':u'â', u'\\^e':u'ê', 
      u'\\^i':u'î', u'\\^o':u'ô', u'\\^u':u'û', u'\\^{A}':u'Â', u'\\^{E}':u'Ê', 
      u'\\^{I}':u'Î', u'\\^{O}':u'Ô', u'\\^{U}':u'Û', u'\\^{\\i}':u'î', 
      u'\\`A':u'À', u'\\`E':u'È', u'\\`I':u'Ì', u'\\`O':u'Ò', u'\\`U':u'Ù', 
      u'\\`\\i':u'ì', u'\\`a':u'à', u'\\`e':u'è', u'\\`i':u'ì', u'\\`o':u'ò', 
      u'\\`u':u'ù', u'\\`{A}':u'À', u'\\`{E}':u'È', u'\\`{I}':u'Ì', 
      u'\\`{O}':u'Ò', u'\\`{U}':u'Ù', u'\\`{\\i}':u'ì', u'\\aa':u'å', 
      u'\\ae':u'æ', u'\\c C':u'Ç', u'\\c c':u'ç', u'\\c {C}':u'Ç', 
      u'\\copyright':u'©', u'\\c{C}':u'Ç', u'\\c{c}':u'ç', u'\\c{{C}}':u'Ç', 
      u'\\dh':u'ð', u'\\emph':u'', u'\\o':u'ø', u'\\r A':u'Å', u'\\r a':u'å', 
      u'\\r {A}':u'Å', u'\\r{A}':u'Å', u'\\r{a}':u'å', u'\\r{{A}}':u'Å', 
      u'\\ss':u'ß', u'\\textordfeminine':u'ª', u'\\textordmasculine':u'º', 
      u'\\textregistered':u'®', u'\\texttrademark':u'™', u'\\th':u'þ', 
      u'\\tt':u'', u'\\~A':u'Ã', u'\\~N':u'Ñ', u'\\~O':u'Õ', u'\\~a':u'ã', 
      u'\\~n':u'ñ', u'\\~o':u'õ', u'\\~{A}':u'Ã', u'\\~{N}':u'Ñ', 
      u'\\~{O}':u'Õ', 
      }

  replaced = {
      u'--':u'—', u'..':u'.', 
      }

class ContainerConfig(object):
  "Configuration class from config file"

  endings = {
      u'Align':u'\\end_layout', u'BarredText':u'\\bar', 
      u'BoldText':u'\\series', u'Cell':u'</cell', 
      u'ChangeDeleted':u'\\change_unchanged', 
      u'ChangeInserted':u'\\change_unchanged', u'ColorText':u'\\color', 
      u'EmphaticText':u'\\emph', u'Hfill':u'\\hfill', u'Inset':u'\\end_inset', 
      u'Layout':u'\\end_layout', u'LyXFooter':u'\\end_document', 
      u'LyXHeader':u'\\end_header', u'Row':u'</row', u'ShapedText':u'\\shape', 
      u'SizeText':u'\\size', u'TextFamily':u'\\family', 
      u'VersalitasText':u'\\noun', 
      }

  extracttext = {
      u'allowed':[u'StringContainer',u'Constant',u'FormulaConstant',], 
      u'cloned':[u'',], 
      u'extracted':[u'PlainLayout',u'TaggedText',u'Align',u'Caption',u'TextFamily',u'EmphaticText',u'VersalitasText',u'BarredText',u'SizeText',u'ColorText',u'LangLine',u'Formula',u'Bracket',u'RawText',], 
      }

  startendings = {
      u'\\begin_deeper':u'\\end_deeper', u'\\begin_inset':u'\\end_inset', 
      u'\\begin_layout':u'\\end_layout', 
      }

  starts = {
      u'':u'StringContainer', u'#LyX':u'BlackBox', u'</lyxtabular':u'BlackBox', 
      u'<cell':u'Cell', u'<column':u'Column', u'<row':u'Row', 
      u'\\align':u'Align', u'\\bar':u'BarredText', 
      u'\\bar default':u'BlackBox', u'\\bar no':u'BlackBox', 
      u'\\begin_body':u'BlackBox', u'\\begin_deeper':u'DeeperList', 
      u'\\begin_document':u'BlackBox', u'\\begin_header':u'LyXHeader', 
      u'\\begin_inset Box':u'BoxInset', u'\\begin_inset Branch':u'Branch', 
      u'\\begin_inset Caption':u'Caption', 
      u'\\begin_inset CommandInset bibitem':u'BiblioEntry', 
      u'\\begin_inset CommandInset bibtex':u'BibTeX', 
      u'\\begin_inset CommandInset citation':u'BiblioCitation', 
      u'\\begin_inset CommandInset href':u'URL', 
      u'\\begin_inset CommandInset include':u'IncludeInset', 
      u'\\begin_inset CommandInset index_print':u'PrintIndex', 
      u'\\begin_inset CommandInset label':u'Label', 
      u'\\begin_inset CommandInset nomencl_print':u'PrintNomenclature', 
      u'\\begin_inset CommandInset nomenclature':u'NomenclatureEntry', 
      u'\\begin_inset CommandInset ref':u'Reference', 
      u'\\begin_inset CommandInset toc':u'TableOfContents', 
      u'\\begin_inset ERT':u'ERT', u'\\begin_inset Flex':u'FlexInset', 
      u'\\begin_inset Flex Chunkref':u'NewfangledChunkRef', 
      u'\\begin_inset Flex Marginnote':u'SideNote', 
      u'\\begin_inset Flex Sidenote':u'SideNote', 
      u'\\begin_inset Flex URL':u'FlexURL', u'\\begin_inset Float':u'Float', 
      u'\\begin_inset FloatList':u'ListOf', u'\\begin_inset Foot':u'Footnote', 
      u'\\begin_inset Formula':u'Formula', 
      u'\\begin_inset FormulaMacro':u'FormulaMacro', 
      u'\\begin_inset Graphics':u'Image', 
      u'\\begin_inset Index':u'IndexReference', 
      u'\\begin_inset Info':u'InfoInset', 
      u'\\begin_inset LatexCommand bibitem':u'BiblioEntry', 
      u'\\begin_inset LatexCommand bibtex':u'BibTeX', 
      u'\\begin_inset LatexCommand cite':u'BiblioCitation', 
      u'\\begin_inset LatexCommand citealt':u'BiblioCitation', 
      u'\\begin_inset LatexCommand citep':u'BiblioCitation', 
      u'\\begin_inset LatexCommand citet':u'BiblioCitation', 
      u'\\begin_inset LatexCommand htmlurl':u'URL', 
      u'\\begin_inset LatexCommand index':u'IndexReference', 
      u'\\begin_inset LatexCommand label':u'Label', 
      u'\\begin_inset LatexCommand nomenclature':u'NomenclatureEntry', 
      u'\\begin_inset LatexCommand prettyref':u'Reference', 
      u'\\begin_inset LatexCommand printindex':u'PrintIndex', 
      u'\\begin_inset LatexCommand printnomenclature':u'PrintNomenclature', 
      u'\\begin_inset LatexCommand ref':u'Reference', 
      u'\\begin_inset LatexCommand tableofcontents':u'TableOfContents', 
      u'\\begin_inset LatexCommand url':u'URL', 
      u'\\begin_inset LatexCommand vref':u'Reference', 
      u'\\begin_inset Marginal':u'SideNote', 
      u'\\begin_inset Newline':u'NewlineInset', 
      u'\\begin_inset Newpage':u'NewPageInset', u'\\begin_inset Note':u'Note', 
      u'\\begin_inset OptArg':u'ShortTitle', 
      u'\\begin_inset Quotes':u'QuoteContainer', 
      u'\\begin_inset Tabular':u'Table', u'\\begin_inset Text':u'InsetText', 
      u'\\begin_inset VSpace':u'VerticalSpace', u'\\begin_inset Wrap':u'Wrap', 
      u'\\begin_inset listings':u'Listing', u'\\begin_inset space':u'Space', 
      u'\\begin_layout':u'Layout', u'\\begin_layout Abstract':u'Abstract', 
      u'\\begin_layout Author':u'Author', 
      u'\\begin_layout Bibliography':u'Bibliography', 
      u'\\begin_layout Chunk':u'NewfangledChunk', 
      u'\\begin_layout Description':u'Description', 
      u'\\begin_layout Enumerate':u'ListItem', 
      u'\\begin_layout Itemize':u'ListItem', u'\\begin_layout List':u'List', 
      u'\\begin_layout LyX-Code':u'LyXCode', 
      u'\\begin_layout Plain':u'PlainLayout', 
      u'\\begin_layout Standard':u'StandardLayout', 
      u'\\begin_layout Title':u'Title', u'\\begin_preamble':u'LyXPreamble', 
      u'\\change_deleted':u'ChangeDeleted', 
      u'\\change_inserted':u'ChangeInserted', 
      u'\\change_unchanged':u'BlackBox', u'\\color':u'ColorText', 
      u'\\color inherit':u'BlackBox', u'\\color none':u'BlackBox', 
      u'\\emph default':u'BlackBox', u'\\emph off':u'BlackBox', 
      u'\\emph on':u'EmphaticText', u'\\emph toggle':u'EmphaticText', 
      u'\\end_body':u'LyXFooter', u'\\family':u'TextFamily', 
      u'\\family default':u'BlackBox', u'\\family roman':u'BlackBox', 
      u'\\hfill':u'Hfill', u'\\labelwidthstring':u'BlackBox', 
      u'\\lang':u'LangLine', u'\\length':u'InsetLength', 
      u'\\lyxformat':u'LyXFormat', u'\\lyxline':u'LyXLine', 
      u'\\newline':u'Newline', u'\\newpage':u'NewPage', 
      u'\\noindent':u'BlackBox', u'\\noun default':u'BlackBox', 
      u'\\noun off':u'BlackBox', u'\\noun on':u'VersalitasText', 
      u'\\paragraph_spacing':u'BlackBox', u'\\series bold':u'BoldText', 
      u'\\series default':u'BlackBox', u'\\series medium':u'BlackBox', 
      u'\\shape':u'ShapedText', u'\\shape default':u'BlackBox', 
      u'\\shape up':u'BlackBox', u'\\size':u'SizeText', 
      u'\\size normal':u'BlackBox', u'\\start_of_appendix':u'StartAppendix', 
      }

  string = {
      u'startcommand':u'\\', 
      }

  table = {
      u'headers':[u'<lyxtabular',u'<features',], 
      }

class EscapeConfig(object):
  "Configuration class from config file"

  chars = {
      u'\n':u'', u' -- ':u' — ', u'\'':u'’', u'---':u'—', u'`':u'‘', 
      }

  commands = {
      u'\\InsetSpace \\space{}':u' ', u'\\InsetSpace \\thinspace{}':u' ', 
      u'\\InsetSpace ~':u' ', u'\\SpecialChar \\-':u'', 
      u'\\SpecialChar \\@.':u'.', u'\\SpecialChar \\ldots{}':u'…', 
      u'\\SpecialChar \\menuseparator':u' ▷ ', 
      u'\\SpecialChar \\nobreakdash-':u'-', u'\\SpecialChar \\slash{}':u'/', 
      u'\\SpecialChar \\textcompwordmark{}':u'', u'\\backslash':u'\\', 
      }

  entities = {
      u'&':u'&amp;', u'<':u'&lt;', u'>':u'&gt;', 
      }

  html = {
      u'/>':u'>', 
      }

  iso885915 = {
      u' ':u'&nbsp;', u' ':u'&emsp;', u' ':u'&#8197;', 
      }

  nonunicode = {
      u' ':u' ', 
      }

class FormulaConfig(object):
  "Configuration class from config file"

  alphacommands = {
      u'\\AA':u'Å', u'\\AE':u'Æ', u'\\L':u'Ł', u'\\O':u'Ø', u'\\OE':u'Œ', 
      u'\\aa':u'å', u'\\ae':u'æ', u'\\alpha':u'α', u'\\beta':u'β', 
      u'\\delta':u'δ', u'\\epsilon':u'ϵ', u'\\eta':u'η', u'\\gamma':u'γ', 
      u'\\i':u'ı', u'\\iota':u'ι', u'\\j':u'ȷ', u'\\kappa':u'κ', u'\\l':u'ł', 
      u'\\lambda':u'λ', u'\\mu':u'μ', u'\\nu':u'ν', u'\\o':u'ø', u'\\oe':u'œ', 
      u'\\omega':u'ω', u'\\phi':u'φ', u'\\pi':u'π', u'\\psi':u'ψ', 
      u'\\rho':u'ρ', u'\\sigma':u'σ', u'\\ss':u'ß', u'\\tau':u'τ', 
      u'\\textcrh':u'ħ', u'\\theta':u'θ', u'\\upsilon':u'υ', 
      u'\\varDelta':u'∆', u'\\varGamma':u'Γ', u'\\varLambda':u'Λ', 
      u'\\varOmega':u'Ω', u'\\varPhi':u'Φ', u'\\varPi':u'Π', u'\\varPsi':u'Ψ', 
      u'\\varSigma':u'Σ', u'\\varTheta':u'Θ', u'\\varUpsilon':u'Υ', 
      u'\\varXi':u'Ξ', u'\\varepsilon':u'ε', u'\\varkappa':u'ϰ', 
      u'\\varphi':u'φ', u'\\varpi':u'ϖ', u'\\varrho':u'ϱ', u'\\varsigma':u'ς', 
      u'\\vartheta':u'ϑ', u'\\xi':u'ξ', u'\\zeta':u'ζ', 
      }

  array = {
      u'begin':u'\\begin', u'cellseparator':u'&', u'end':u'\\end', 
      u'rowseparator':u'\\\\', 
      }

  combiningfunctions = {
      u'\\acute':u'́', u'\\bar':u'̄', u'\\breve':u'̆', u'\\c':u'̧', 
      u'\\check':u'̌', u'\\dddot':u'⃛', u'\\ddot':u'̈', u'\\dot':u'̇', 
      u'\\grave':u'̀', u'\\hat':u'̂', u'\\mathring':u'̊', 
      u'\\overleftarrow':u'⃖', u'\\overrightarrow':u'⃗', u'\\r':u'̥', 
      u'\\s':u'̩', u'\\textsubring':u'̥', u'\\tilde':u'̃', u'\\vec':u'⃗', 
      }

  commands = {
      u'\\ ':u' ', u'\\!':u'', u'\\$':u'$', u'\\%':u'%', u'\\,':u' ', 
      u'\\:':u' ', u'\\;':u' ', u'\\APLdownarrowbox':u'⍗', 
      u'\\APLleftarrowbox':u'⍇', u'\\APLrightarrowbox':u'⍈', 
      u'\\APLuparrowbox':u'⍐', u'\\Box':u'□', u'\\Bumpeq':u'≎', 
      u'\\CIRCLE':u'●', u'\\Cap':u'⋒', u'\\CheckedBox':u'☑', u'\\Circle':u'○', 
      u'\\Coloneqq':u'⩴', u'\\Corresponds':u'≙', u'\\Cup':u'⋓', 
      u'\\Delta':u'Δ', u'\\Diamond':u'◇', u'\\Downarrow':u'⇓', u'\\EUR':u'€', 
      u'\\Gamma':u'Γ', u'\\Im':u'ℑ', u'\\Join':u'⨝', u'\\LEFTCIRCLE':u'◖', 
      u'\\LEFTcircle':u'◐', u'\\Lambda':u'Λ', u'\\Leftarrow':u'⇐', 
      u'\\Leftrightarrow':u' ⇔ ', u'\\Lleftarrow':u'⇚', 
      u'\\Longleftarrow':u'⟸', u'\\Longleftrightarrow':u'⟺', 
      u'\\Longrightarrow':u'⟹', u'\\Lsh':u'↰', u'\\Mapsfrom':u'⇐|', 
      u'\\Mapsto':u'|⇒', u'\\Omega':u'Ω', u'\\P':u'¶', u'\\Phi':u'Φ', 
      u'\\Pi':u'Π', u'\\Pr':u'Pr', u'\\Psi':u'Ψ', u'\\RIGHTCIRCLE':u'◗', 
      u'\\RIGHTcircle':u'◑', u'\\Re':u'ℜ', u'\\Rightarrow':u' ⇒ ', 
      u'\\Rrightarrow':u'⇛', u'\\Rsh':u'↱', u'\\S':u'§', u'\\Sigma':u'Σ', 
      u'\\Square':u'☐', u'\\Subset':u'⋐', u'\\Supset':u'⋑', u'\\Theta':u'Θ', 
      u'\\Uparrow':u'⇑', u'\\Updownarrow':u'⇕', u'\\Upsilon':u'Υ', 
      u'\\Vdash':u'⊩', u'\\Vert':u'∥', u'\\Vvdash':u'⊪', u'\\XBox':u'☒', 
      u'\\Xi':u'Ξ', u'\\Yup':u'⅄', u'\\\\':u'<br/>', u'\\_':u'_', 
      u'\\aleph':u'ℵ', u'\\amalg':u'∐', u'\\angle':u'∠', u'\\approx':u' ≈ ', 
      u'\\aquarius':u'♒', u'\\arccos':u'arccos', u'\\arcsin':u'arcsin', 
      u'\\arctan':u'arctan', u'\\arg':u'arg', u'\\aries':u'♈', u'\\ast':u'∗', 
      u'\\asymp':u'≍', u'\\backepsilon':u'∍', u'\\backprime':u'‵', 
      u'\\backsimeq':u'⋍', u'\\backslash':u'\\', u'\\barwedge':u'⊼', 
      u'\\because':u'∵', u'\\beth':u'ℶ', u'\\between':u'≬', u'\\bigcap':u'∩', 
      u'\\bigcirc':u'○', u'\\bigcup':u'∪', u'\\bigodot':u'⊙', 
      u'\\bigoplus':u'⊕', u'\\bigotimes':u'⊗', u'\\bigsqcup':u'⊔', 
      u'\\bigstar':u'★', u'\\bigtriangledown':u'▽', u'\\bigtriangleup':u'△', 
      u'\\biguplus':u'⊎', u'\\bigvee':u'∨', u'\\bigwedge':u'∧', 
      u'\\blacklozenge':u'⧫', u'\\blacksmiley':u'☻', u'\\blacksquare':u'■', 
      u'\\blacktriangle':u'▲', u'\\blacktriangledown':u'▼', 
      u'\\blacktriangleright':u'▶', u'\\bot':u'⊥', u'\\bowtie':u'⋈', 
      u'\\box':u'▫', u'\\boxdot':u'⊡', u'\\bullet':u'•', u'\\bumpeq':u'≏', 
      u'\\cancer':u'♋', u'\\cap':u'∩', u'\\capricornus':u'♑', u'\\cdot':u'⋅', 
      u'\\cdots':u'⋯', u'\\centerdot':u'∙', u'\\checkmark':u'✓', u'\\chi':u'χ', 
      u'\\circ':u'○', u'\\circeq':u'≗', u'\\circledR':u'®', 
      u'\\circledast':u'⊛', u'\\circledcirc':u'⊚', u'\\circleddash':u'⊝', 
      u'\\clubsuit':u'♣', u'\\coloneqq':u'≔', u'\\complement':u'∁', 
      u'\\cong':u'≅', u'\\coprod':u'∐', u'\\copyright':u'©', u'\\cos':u'cos', 
      u'\\cosh':u'cosh', u'\\cot':u'cot', u'\\coth':u'coth', u'\\csc':u'csc', 
      u'\\cup':u'∪', u'\\curvearrowleft':u'↶', u'\\curvearrowright':u'↷', 
      u'\\dag':u'†', u'\\dagger':u'†', u'\\daleth':u'ℸ', 
      u'\\dashleftarrow':u'⇠', u'\\dashrightarrow':u' ⇢ ', u'\\dashv':u'⊣', 
      u'\\ddag':u'‡', u'\\ddagger':u'‡', u'\\ddots':u'⋱', u'\\deg':u'deg', 
      u'\\det':u'det', u'\\diagdown':u'╲', u'\\diagup':u'╱', u'\\diamond':u'◇', 
      u'\\diamondsuit':u'♦', u'\\dim':u'dim', u'\\displaystyle':u'', 
      u'\\div':u'÷', u'\\divideontimes':u'⋇', u'\\dotdiv':u'∸', 
      u'\\doteq':u'≐', u'\\doteqdot':u'≑', u'\\dotplus':u'∔', u'\\dots':u'…', 
      u'\\doublebarwedge':u'⌆', u'\\downarrow':u'↓', u'\\downdownarrows':u'⇊', 
      u'\\downharpoonleft':u'⇃', u'\\downharpoonright':u'⇂', u'\\earth':u'♁', 
      u'\\ell':u'ℓ', u'\\emptyset':u'∅', u'\\eqcirc':u'≖', u'\\eqcolon':u'≕', 
      u'\\eqsim':u'≂', u'\\equiv':u' ≡ ', u'\\euro':u'€', u'\\exists':u'∃', 
      u'\\exp':u'exp', u'\\fallingdotseq':u'≒', u'\\female':u'♀', 
      u'\\flat':u'♭', u'\\forall':u'∀', u'\\frown':u'⌢', u'\\frownie':u'☹', 
      u'\\gcd':u'gcd', u'\\ge':u' ≥ ', u'\\gemini':u'♊', u'\\geq':u' ≥ ', 
      u'\\geq)':u'≥', u'\\geqq':u'≧', u'\\geqslant':u'≥', u'\\gets':u'←', 
      u'\\gg':u'≫', u'\\ggg':u'⋙', u'\\gimel':u'ℷ', u'\\gneqq':u'≩', 
      u'\\gnsim':u'⋧', u'\\gtrdot':u'⋗', u'\\gtreqless':u'⋚', 
      u'\\gtreqqless':u'⪌', u'\\gtrless':u'≷', u'\\gtrsim':u'≳', 
      u'\\hbar':u'ℏ', u'\\heartsuit':u'♥', 
      u'\\hfill':u'<span class="hfill"> </span>', u'\\hom':u'hom', 
      u'\\hookleftarrow':u'↩', u'\\hookrightarrow':u'↪', u'\\hslash':u'ℏ', 
      u'\\idotsint':u'<span class="bigsymbol">∫⋯∫</span>', 
      u'\\iiint':u'<span class="bigsymbol">∭</span>', 
      u'\\iint':u'<span class="bigsymbol">∬</span>', u'\\imath':u'ı', 
      u'\\implies':u'  ⇒  ', u'\\in':u' ∈ ', u'\\inf':u'inf', u'\\infty':u'∞', 
      u'\\int':u'<span class="bigsymbol">∫</span>', 
      u'\\intop':u'<span class="bigsymbol">∫</span>', u'\\invneg':u'⌐', 
      u'\\jmath':u'ȷ', u'\\jupiter':u'♃', u'\\ker':u'ker', u'\\land':u'∧', 
      u'\\landupint':u'<span class="bigsymbol">∱</span>', u'\\langle':u'⟨', 
      u'\\lbrace':u'{', u'\\lbrace)':u'{', u'\\lbrack':u'[', u'\\lceil':u'⌈', 
      u'\\ldots':u'…', u'\\le':u'≤', u'\\leadsto':u'⇝', u'\\leftarrow':u' ← ', 
      u'\\leftarrow)':u'←', u'\\leftarrowtail':u'↢', u'\\leftarrowtobar':u'⇤', 
      u'\\leftharpoondown':u'↽', u'\\leftharpoonup':u'↼', 
      u'\\leftleftarrows':u'⇇', u'\\leftleftharpoons':u'⥢', u'\\leftmoon':u'☾', 
      u'\\leftrightarrow':u'↔', u'\\leftrightarrows':u'⇆', 
      u'\\leftrightharpoons':u'⇋', u'\\leftthreetimes':u'⋋', u'\\leo':u'♌', 
      u'\\leq':u' ≤ ', u'\\leq)':u'≤', u'\\leqq':u'≦', u'\\leqslant':u'≤', 
      u'\\lessdot':u'⋖', u'\\lesseqgtr':u'⋛', u'\\lesseqqgtr':u'⪋', 
      u'\\lessgtr':u'≶', u'\\lesssim':u'≲', u'\\lfloor':u'⌊', u'\\lg':u'lg', 
      u'\\lhd':u'⊲', u'\\libra':u'♎', u'\\lightning':u'↯', u'\\lim':u'lim', 
      u'\\liminf':u'liminf', u'\\limsup':u'limsup', u'\\ll':u'≪', 
      u'\\lll':u'⋘', u'\\ln':u'ln', u'\\lneqq':u'≨', u'\\lnot':u'¬', 
      u'\\lnsim':u'⋦', u'\\log':u'log', u'\\longleftarrow':u'⟵', 
      u'\\longleftrightarrow':u'⟷', u'\\longmapsto':u'⟼', 
      u'\\longrightarrow':u'⟶', u'\\looparrowleft':u'↫', 
      u'\\looparrowright':u'↬', u'\\lor':u'∨', u'\\lozenge':u'◊', 
      u'\\ltimes':u'⋉', u'\\lyxlock':u'', u'\\male':u'♂', u'\\maltese':u'✠', 
      u'\\mapsfrom':u'↤', u'\\mapsto':u'↦', u'\\mathcircumflex':u'^', 
      u'\\max':u'max', u'\\measuredangle':u'∡', u'\\mercury':u'☿', 
      u'\\mho':u'℧', u'\\mid':u'∣', u'\\min':u'min', u'\\models':u'⊨', 
      u'\\mp':u'∓', u'\\multimap':u'⊸', u'\\nLeftarrow':u'⇍', 
      u'\\nLeftrightarrow':u'⇎', u'\\nRightarrow':u'⇏', u'\\nVDash':u'⊯', 
      u'\\nabla':u'∇', u'\\napprox':u'≉', u'\\natural':u'♮', u'\\ncong':u'≇', 
      u'\\ne':u' ≠ ', u'\\nearrow':u'↗', u'\\neg':u'¬', u'\\neg)':u'¬', 
      u'\\neptune':u'♆', u'\\neq':u' ≠ ', u'\\nequiv':u'≢', u'\\nexists':u'∄', 
      u'\\ngeqslant':u'≱', u'\\ngtr':u'≯', u'\\ngtrless':u'≹', u'\\ni':u'∋', 
      u'\\ni)':u'∋', u'\\nleftarrow':u'↚', u'\\nleftrightarrow':u'↮', 
      u'\\nleqslant':u'≰', u'\\nless':u'≮', u'\\nlessgtr':u'≸', u'\\nmid':u'∤', 
      u'\\nonumber':u'', u'\\not':u'¬', u'\\not<':u'≮', u'\\not=':u'≠', 
      u'\\not>':u'≯', u'\\not\\in':u' ∉ ', u'\\notbackslash':u'⍀', 
      u'\\notin':u'∉', u'\\notni':u'∌', u'\\notslash':u'⌿', 
      u'\\nparallel':u'∦', u'\\nprec':u'⊀', u'\\nrightarrow':u'↛', 
      u'\\nsim':u'≁', u'\\nsimeq':u'≄', u'\\nsqsubset':u'⊏̸', 
      u'\\nsubseteq':u'⊈', u'\\nsucc':u'⊁', u'\\nsucccurlyeq':u'⋡', 
      u'\\nsupset':u'⊅', u'\\nsupseteq':u'⊉', u'\\ntriangleleft':u'⋪', 
      u'\\ntrianglelefteq':u'⋬', u'\\ntriangleright':u'⋫', 
      u'\\ntrianglerighteq':u'⋭', u'\\nvDash':u'⊭', u'\\nvdash':u'⊬', 
      u'\\nwarrow':u'↖', u'\\odot':u'⊙', u'\\officialeuro':u'€', 
      u'\\oiiint':u'<span class="bigsymbol">∰</span>', 
      u'\\oiint':u'<span class="bigsymbol">∯</span>', 
      u'\\oint':u'<span class="bigsymbol">∮</span>', 
      u'\\ointclockwise':u'<span class="bigsymbol">∲</span>', 
      u'\\ointctrclockwise':u'<span class="bigsymbol">∳</span>', 
      u'\\ominus':u'⊖', u'\\oplus':u'⊕', u'\\oslash':u'⊘', u'\\otimes':u'⊗', 
      u'\\owns':u'∋', u'\\parallel':u'∥', u'\\partial':u'∂', u'\\perp':u'⊥', 
      u'\\pisces':u'♓', u'\\pitchfork':u'⋔', u'\\pluto':u'♇', u'\\pm':u'±', 
      u'\\pointer':u'➪', u'\\pounds':u'£', u'\\prec':u'≺', 
      u'\\preccurlyeq':u'≼', u'\\preceq':u'≼', u'\\precsim':u'≾', 
      u'\\prime':u'′', u'\\prod':u'<span class="bigsymbol">∏</span>', 
      u'\\prompto':u'∝', u'\\propto':u' ∝ ', u'\\qquad':u'  ', u'\\quad':u' ', 
      u'\\quarternote':u'♩', u'\\rangle':u'⟩', u'\\rbrace':u'}', 
      u'\\rbrace)':u'}', u'\\rbrack':u']', u'\\rceil':u'⌉', u'\\rfloor':u'⌋', 
      u'\\rhd':u'⊳', u'\\rightarrow':u' → ', u'\\rightarrow)':u'→', 
      u'\\rightarrowtail':u'↣', u'\\rightarrowtobar':u'⇥', 
      u'\\rightharpoondown':u'⇁', u'\\rightharpoonup':u'⇀', 
      u'\\rightharpooondown':u'⇁', u'\\rightharpooonup':u'⇀', 
      u'\\rightleftarrows':u'⇄', u'\\rightleftharpoons':u'⇌', 
      u'\\rightmoon':u'☽', u'\\rightrightarrows':u'⇉', 
      u'\\rightrightharpoons':u'⥤', u'\\rightsquigarrow':u' ⇝ ', 
      u'\\rightthreetimes':u'⋌', u'\\risingdotseq':u'≓', u'\\rtimes':u'⋊', 
      u'\\sagittarius':u'♐', u'\\saturn':u'♄', u'\\scorpio':u'♏', 
      u'\\scriptscriptstyle':u'', u'\\scriptstyle':u'', u'\\searrow':u'↘', 
      u'\\sec':u'sec', u'\\setminus':u'∖', u'\\sharp':u'♯', u'\\sim':u' ~ ', 
      u'\\simeq':u'≃', u'\\sin':u'sin', u'\\sinh':u'sinh', u'\\slash':u'∕', 
      u'\\smile':u'⌣', u'\\smiley':u'☺', u'\\spadesuit':u'♠', 
      u'\\sphericalangle':u'∢', u'\\sqcap':u'⊓', u'\\sqcup':u'⊔', 
      u'\\sqsubset':u'⊏', u'\\sqsubseteq':u'⊑', u'\\sqsupset':u'⊐', 
      u'\\sqsupseteq':u'⊒', u'\\square':u'□', u'\\star':u'⋆', 
      u'\\subset':u' ⊂ ', u'\\subseteq':u'⊆', u'\\subseteqq':u'⫅', 
      u'\\subsetneqq':u'⫋', u'\\succ':u'≻', u'\\succcurlyeq':u'≽', 
      u'\\succeq':u'≽', u'\\succnsim':u'⋩', u'\\succsim':u'≿', 
      u'\\sum':u'<span class="bigsymbol">∑</span>', u'\\sun':u'☼', 
      u'\\sup':u'sup', u'\\supset':u' ⊃ ', u'\\supseteq':u'⊇', 
      u'\\supseteqq':u'⫆', u'\\supsetneqq':u'⫌', u'\\surd':u'√', 
      u'\\swarrow':u'↙', u'\\tan':u'tan', u'\\tanh':u'tanh', u'\\taurus':u'♉', 
      u'\\textasciicircum':u'^', u'\\textasciitilde':u'~', 
      u'\\textbackslash':u'\\', u'\\textendash':u'—', u'\\textgreater':u'>', 
      u'\\textless':u'<', u'\\textquotedblleft':u'“', 
      u'\\textquotedblright':u'”', u'\\textstyle':u'', u'\\therefore':u'∴', 
      u'\\times':u' × ', u'\\to':u'→', u'\\top':u'⊤', u'\\triangle':u'△', 
      u'\\triangleleft':u'⊲', u'\\trianglelefteq':u'⊴', u'\\triangleq':u'≜', 
      u'\\triangleright':u'▷', u'\\trianglerighteq':u'⊵', 
      u'\\twoheadleftarrow':u'↞', u'\\twoheadrightarrow':u'↠', 
      u'\\twonotes':u'♫', u'\\udot':u'⊍', u'\\unlhd':u'⊴', u'\\unrhd':u'⊵', 
      u'\\unrhl':u'⊵', u'\\uparrow':u'↑', u'\\updownarrow':u'↕', 
      u'\\upharpoonleft':u'↿', u'\\upharpoonright':u'↾', u'\\uplus':u'⊎', 
      u'\\upuparrows':u'⇈', u'\\uranus':u'♅', u'\\vDash':u'⊨', 
      u'\\varclubsuit':u'♧', u'\\vardiamondsuit':u'♦', u'\\varheartsuit':u'♥', 
      u'\\varnothing':u'∅', u'\\varspadesuit':u'♤', u'\\vdash':u'⊢', 
      u'\\vdots':u'⋮', u'\\vee':u'∨', u'\\vee)':u'∨', u'\\veebar':u'⊻', 
      u'\\vert':u'∣', u'\\virgo':u'♍', u'\\wedge':u'∧', u'\\wedge)':u'∧', 
      u'\\wp':u'℘', u'\\wr':u'≀', u'\\yen':u'¥', u'\\{':u'{', u'\\|':u'∥', 
      u'\\}':u'}', 
      }

  decoratingfunctions = {
      u'\\overleftarrow':u'⟵', u'\\overrightarrow':u'⟶', u'\\widehat':u'^', 
      }

  definingfunctions = {
      u'\\newcommand':u'[$n!][$1][$2][$3][$4][$5][$6][$7][$8][$9]{$d}', 
      u'\\renewcommand':u'[$n!][$1][$2][$3][$4][$5][$6][$7][$8][$9]{$d}', 
      }

  endings = {
      u'bracket':u'}', u'complex':u'\\]', u'endafter':u'}', 
      u'endbefore':u'\\end{', u'squarebracket':u']', 
      }

  environments = {
      u'align':[u'r',u'l',], u'eqnarray':[u'r',u'c',u'l',], 
      u'gathered':[u'l',u'l',], 
      }

  fontfunctions = {
      u'\\boldsymbol':u'b', u'\\mathbb':u'span class="blackboard"', 
      u'\\mathbb{A}':u'𝔸', u'\\mathbb{B}':u'𝔹', u'\\mathbb{C}':u'ℂ', 
      u'\\mathbb{D}':u'𝔻', u'\\mathbb{E}':u'𝔼', u'\\mathbb{F}':u'𝔽', 
      u'\\mathbb{G}':u'𝔾', u'\\mathbb{H}':u'ℍ', u'\\mathbb{J}':u'𝕁', 
      u'\\mathbb{K}':u'𝕂', u'\\mathbb{L}':u'𝕃', u'\\mathbb{N}':u'ℕ', 
      u'\\mathbb{O}':u'𝕆', u'\\mathbb{P}':u'ℙ', u'\\mathbb{Q}':u'ℚ', 
      u'\\mathbb{R}':u'ℝ', u'\\mathbb{S}':u'𝕊', u'\\mathbb{T}':u'𝕋', 
      u'\\mathbb{W}':u'𝕎', u'\\mathbb{Z}':u'ℤ', u'\\mathbf':u'b', 
      u'\\mathcal':u'span class="script"', 
      u'\\mathfrak':u'span class="fraktur"', u'\\mathfrak{C}':u'ℭ', 
      u'\\mathfrak{F}':u'𝔉', u'\\mathfrak{H}':u'ℌ', u'\\mathfrak{I}':u'ℑ', 
      u'\\mathfrak{R}':u'ℜ', u'\\mathfrak{Z}':u'ℨ', u'\\mathit':u'i', 
      u'\\mathring{A}':u'Å', u'\\mathring{U}':u'Ů', u'\\mathring{a}':u'å', 
      u'\\mathring{u}':u'ů', u'\\mathring{w}':u'ẘ', u'\\mathring{y}':u'ẙ', 
      u'\\mathrm':u'span class="mathrm"', u'\\mathscr':u'span class="script"', 
      u'\\mathscr{B}':u'ℬ', u'\\mathscr{E}':u'ℰ', u'\\mathscr{F}':u'ℱ', 
      u'\\mathscr{H}':u'ℋ', u'\\mathscr{I}':u'ℐ', u'\\mathscr{L}':u'ℒ', 
      u'\\mathscr{M}':u'ℳ', u'\\mathscr{R}':u'ℛ', 
      u'\\mathsf':u'span class="mathsf"', u'\\mathtt':u'tt', 
      }

  hybridfunctions = {
      
      u'\\binom':[u'{$1}{$2}',u'f3{(}f0{f1{$1}f2{$2}}f3{)}',u'span class="binom"',u'span class="upbinom"',u'span class="downbinom"',u'span class="bigsymbol"',], 
      u'\\boxed':[u'{$1}',u'f0{$1}',u'span class="boxed"',], 
      u'\\cfrac':[u'[$p!]{$1}{$2}',u'f0{f1{$1}f2{$2}}',u'span class="fullfraction"',u'span class="numerator$p"',u'span class="denominator"',], 
      u'\\color':[u'{$p!}{$1}',u'f0{$1}',u'span style="color: $p;"',], 
      u'\\colorbox':[u'{$p!}{$1}',u'f0{$1}',u'span class="colorbox" style="background: $p;"',], 
      u'\\dbinom':[u'{$1}{$2}',u'f3{(}f0{f1{$1}f2{$2}}f3{)}',u'span class="fullbinom"',u'span class="upbinom"',u'span class="downbinom"',u'span class="bigsymbol"',], 
      u'\\dfrac':[u'{$1}{$2}',u'f0{f1{$1}f2{$2}}',u'span class="fullfraction"',u'span class="numerator"',u'span class="denominator"',], 
      u'\\fbox':[u'{$1}',u'f0{$1}',u'span class="fbox"',], 
      u'\\fcolorbox':[u'{$p!}{$q!}{$1}',u'f0{$1}',u'span class="boxed" style="border-color: $p; background: $q;"',], 
      u'\\frac':[u'{$1}{$2}',u'f0{f1{$1}f2{$2}}',u'span class="fraction"',u'span class="numerator"',u'span class="denominator"',], 
      u'\\framebox':[u'[$p!][$q!]{$1}',u'f0{$1}',u'span class="framebox-$q" style="width: $p;"',], 
      u'\\hspace':[u'{$p!}',u'f0{ }',u'span class="hspace" style="width: $p;"',], 
      u'\\leftroot':[u'{$p!}',u'f0{ }',u'span class="leftroot" style="width: $p;px"',], 
      u'\\nicefrac':[u'{$1}{$2}',u'f0{f1{$1}⁄f2{$2}}',u'span class="fraction"',u'sup class="numerator"',u'sub class="denominator"',], 
      u'\\raisebox':[u'{$p!}{$1}',u'f0{$1}',u'span class="raisebox" style="vertical-align: $p;"',], 
      u'\\renewenvironment':[u'{$1!}{$2!}{$3!}',u'',], 
      u'\\sqrt':[u'[$0]{$1}',u'f1{$0}f0{f2{√}f3{$1}}',u'span class="sqrt"',u'sup',u'span class="radical"',u'span class="root"',], 
      u'\\stackrel':[u'{$1}{$2}',u'f0{f1{$1}f2{$2}}',u'span class="stackrel"',u'span class="upstackrel"',u'span class="downstackrel"',], 
      u'\\tbinom':[u'{$1}{$2}',u'f3{(}f0{f1{$1}f2{$2}}f3{)}',u'span class="fullbinom"',u'span class="upbinom"',u'span class="downbinom"',u'span class="bigsymbol"',], 
      u'\\textcolor':[u'{$p!}{$1}',u'f0{$1}',u'span style="color: $p;"',], 
      u'\\unit':[u'[$0]{$1}',u'$0f0{$1.font}',u'span class="unit"',], 
      u'\\unitfrac':[u'[$0]{$1}{$2}',u'$0f0{f1{$1.font}⁄f2{$2.font}}',u'span class="fraction"',u'sup class="unit"',u'sub class="unit"',], 
      u'\\uproot':[u'{$p!}',u'f0{ }',u'span class="uproot" style="width: $p;px"',], 
      u'\\vspace':[u'{$p!}',u'f0{ }',u'span class="vspace" style="height: $p;"',], 
      }

  labelfunctions = {
      u'\\label':u'a name="#"', 
      }

  limits = {
      u'commands':[u'\\sum',u'\\int',u'\\intop',], u'operands':[u'^',u'_',], 
      }

  modified = {
      u'\n':u'', u' ':u'', u'$':u'', u'&':u'    ', u'\'':u'’', u'+':u' + ', 
      u',':u', ', u'-':u' − ', u'/':u' ⁄ ', u'<':u' &lt; ', u'=':u' = ', 
      u'>':u' &gt; ', u'@':u'', u'~':u'', 
      }

  onefunctions = {
      u'\\Big':u'span class="bigsymbol"', u'\\Bigg':u'span class="hugesymbol"', 
      u'\\bar':u'span class="bar"', u'\\begin{array}':u'span class="arraydef"', 
      u'\\big':u'span class="symbol"', u'\\bigg':u'span class="largesymbol"', 
      u'\\bigl':u'span class="bigsymbol"', u'\\bigr':u'span class="bigsymbol"', 
      u'\\ensuremath':u'span class="ensuremath"', 
      u'\\hphantom':u'span class="phantom"', u'\\left':u'span class="symbol"', 
      u'\\left.':u'<span class="leftdot"></span>', 
      u'\\middle':u'span class="symbol"', 
      u'\\overbrace':u'span class="overbrace"', 
      u'\\overline':u'span class="overline"', 
      u'\\phantom':u'span class="phantom"', u'\\right':u'span class="symbol"', 
      u'\\right.':u'<span class="rightdot"></span>', 
      u'\\underbrace':u'span class="underbrace"', u'\\underline':u'u', 
      u'\\vphantom':u'span class="phantom"', 
      }

  preamblefunctions = {
      u'\\setcounter':[u'{$p!}{$n!}',u'setcounter',], 
      }

  starts = {
      u'beginafter':u'}', u'beginbefore':u'\\begin{', u'bracket':u'{', 
      u'command':u'\\', u'comment':u'%', u'complex':u'\\[', u'simple':u'$', 
      u'squarebracket':u'[', u'unnumbered':u'*', 
      }

  symbolfunctions = {
      u'^':u'sup', u'_':u'sub', 
      }

  textfunctions = {
      u'\\mbox':u'span class="mbox"', u'\\text':u'span class="text"', 
      u'\\textbf':u'b', u'\\textipa':u'span class="textipa"', u'\\textit':u'i', 
      u'\\textnormal':u'span class="textnormal"', 
      u'\\textrm':u'span class="textrm"', 
      u'\\textsc':u'span class="versalitas"', 
      u'\\textsf':u'span class="textsf"', u'\\textsl':u'i', u'\\texttt':u'tt', 
      u'\\textup':u'span class="normal"', 
      }

  unmodified = {
      
      u'characters':[u'.',u'*',u'€',u'(',u')',u'[',u']',u':',u'·',u'!',u';',u'|',u'§',u'"',], 
      }

class GeneralConfig(object):
  "Configuration class from config file"

  version = {
      u'date':u'2010-11-23', u'lyxformat':u'398', u'number':u'1.1.0', 
      }

class HeaderConfig(object):
  "Configuration class from config file"

  parameters = {
      u'beginpreamble':u'\\begin_preamble', u'branch':u'\\branch', 
      u'documentclass':u'\\textclass', u'endbranch':u'\\end_branch', 
      u'endpreamble':u'\\end_preamble', u'language':u'\\language', 
      u'lstset':u'\\lstset', u'outputchanges':u'\\output_changes', 
      u'paragraphseparation':u'\\paragraph_separation', 
      u'pdftitle':u'\\pdf_title', u'secnumdepth':u'\\secnumdepth', 
      u'tocdepth':u'\\tocdepth', 
      }

  styles = {
      
      u'article':[u'article',u'aastex',u'aapaper',u'acmsiggraph',u'sigplanconf',u'achemso',u'amsart',u'apa',u'arab-article',u'armenian-article',u'article-beamer',u'chess',u'dtk',u'elsarticle',u'heb-article',u'IEEEtran',u'iopart',u'kluwer',u'scrarticle-beamer',u'scrartcl',u'extarticle',u'paper',u'mwart',u'revtex4',u'spie',u'svglobal3',u'ltugboat',u'agu-dtd',u'jgrga',u'agums',u'entcs',u'egs',u'ijmpc',u'ijmpd',u'singlecol-new',u'doublecol-new',u'isprs',u'tarticle',u'jsarticle',u'jarticle',u'jss',u'literate-article',u'siamltex',u'cl2emult',u'llncs',u'svglobal',u'svjog',u'svprobth',], 
      u'book':[u'book',u'amsbook',u'scrbook',u'extbook',u'tufte-book',u'report',u'extreport',u'scrreprt',u'memoir',u'tbook',u'jsbook',u'jbook',u'mwbk',u'svmono',u'svmult',u'treport',u'jreport',u'mwrep',], 
      }

class ImageConfig(object):
  "Configuration class from config file"

  converters = {
      
      u'imagemagick':u'convert[ -density $scale][ -define $format:use-cropbox=true] "$input" "$output"', 
      u'inkscape':u'inkscape "$input" --export-png="$output"', 
      }

  cropboxformats = {
      u'.eps':u'ps', u'.pdf':u'pdf', u'.ps':u'ps', 
      }

  formats = {
      u'default':u'.png', u'vector':[u'.svg',u'.eps',], 
      }

class LayoutConfig(object):
  "Configuration class from config file"

  groupable = {
      
      u'allowed':[u'StringContainer',u'Constant',u'TaggedText',u'Align',u'TextFamily',u'EmphaticText',u'VersalitasText',u'BarredText',u'SizeText',u'ColorText',u'LangLine',u'Formula',], 
      }

class NewfangleConfig(object):
  "Configuration class from config file"

  constants = {
      u'chunkref':u'chunkref{', u'endcommand':u'}', u'endmark':u'&gt;', 
      u'startcommand':u'\\', u'startmark':u'=&lt;', 
      }

class NumberingConfig(object):
  "Configuration class from config file"

  layouts = {
      
      u'ordered':[u'Chapter',u'Section',u'Subsection',u'Subsubsection',u'Paragraph',], 
      u'roman':[u'Part',u'Book',], 
      }

  sequence = {
      u'symbols':[u'*',u'**',u'†',u'‡',u'§',u'§§',u'¶',u'¶¶',u'#',u'##',], 
      }

class StyleConfig(object):
  "Configuration class from config file"

  hspaces = {
      u'\\enskip{}':u' ', u'\\hfill{}':u'<span class="hfill"> </span>', 
      u'\\hspace*{\\fill}':u' ', u'\\hspace*{}':u'', u'\\hspace{}':u' ', 
      u'\\negthinspace{}':u'', u'\\qquad{}':u'  ', u'\\quad{}':u' ', 
      u'\\space{}':u' ', u'\\thinspace{}':u' ', u'~':u' ', 
      }

  quotes = {
      u'ald':u'»', u'als':u'›', u'ard':u'«', u'ars':u'‹', u'eld':u'“', 
      u'els':u'‘', u'erd':u'”', u'ers':u'’', u'fld':u'«', u'fls':u'‹', 
      u'frd':u'»', u'frs':u'›', u'gld':u'„', u'gls':u'‚', u'grd':u'“', 
      u'grs':u'‘', u'pld':u'„', u'pls':u'‚', u'prd':u'”', u'prs':u'’', 
      u'sld':u'”', u'srd':u'”', 
      }

  size = {
      u'ignoredtexts':[u'col',u'text',u'line',u'page',u'theight',u'pheight',], 
      }

  vspaces = {
      u'bigskip':u'<div class="bigskip"> </div>', 
      u'defskip':u'<div class="defskip"> </div>', 
      u'medskip':u'<div class="medskip"> </div>', 
      u'smallskip':u'<div class="smallskip"> </div>', 
      u'vfill':u'<div class="vfill"> </div>', 
      }

class TOCConfig(object):
  "Configuration class from config file"

  extractplain = {
      
      u'allowed':[u'StringContainer',u'Constant',u'TaggedText',u'Align',u'TextFamily',u'EmphaticText',u'VersalitasText',u'BarredText',u'SizeText',u'ColorText',u'LangLine',u'Formula',], 
      u'cloned':[u'',], u'extracted':[u'',], 
      }

  extracttitle = {
      u'allowed':[u'StringContainer',u'Constant',u'Space',], 
      u'cloned':[u'TextFamily',u'EmphaticText',u'VersalitasText',u'BarredText',u'SizeText',u'ColorText',u'LangLine',u'Formula',], 
      u'extracted':[u'PlainLayout',u'TaggedText',u'Align',u'Caption',u'StandardLayout',], 
      }

class TagConfig(object):
  "Configuration class from config file"

  barred = {
      u'under':u'u', 
      }

  family = {
      u'sans':u'span class="sans"', u'typewriter':u'tt', 
      }

  flex = {
      u'CharStyle:Code':u'span class="code"', 
      u'CharStyle:MenuItem':u'span class="menuitem"', 
      }

  group = {
      u'layouts':[u'Quotation',u'Quote',], 
      }

  layouts = {
      u'Center':u'div', u'Chapter':u'h?', u'Date':u'h2', u'Paragraph':u'div', 
      u'Part':u'h1', u'Quotation':u'blockquote', u'Quote':u'blockquote', 
      u'Section':u'h?', u'Subsection':u'h?', u'Subsubsection':u'h?', 
      }

  listitems = {
      u'Enumerate':u'ol', u'Itemize':u'ul', 
      }

  notes = {
      u'Comment':u'', u'Greyedout':u'span class="greyedout"', u'Note':u'', 
      }

  shaped = {
      u'italic':u'i', u'slanted':u'i', u'smallcaps':u'span class="versalitas"', 
      }

class TranslationConfig(object):
  "Configuration class from config file"

  constants = {
      u'Appendix':u'Appendix', u'Book':u'Book', u'Chapter':u'Chapter', 
      u'Paragraph':u'Paragraph', u'Part':u'Part', u'Section':u'Section', 
      u'Subsection':u'Subsection', u'Subsubsection':u'Subsubsection', 
      u'abstract':u'Abstract', u'bibliography':u'Bibliography', 
      u'figure':u'figure', u'float-algorithm':u'Algorithm ', 
      u'float-figure':u'Figure ', u'float-listing':u'Listing ', 
      u'float-table':u'Table ', u'float-tableau':u'Tableau ', 
      u'footnotes':u'Footnotes', u'generated-by':u'Document generated by ', 
      u'generated-on':u' on ', u'index':u'Index', 
      u'jsmath-enable':u'Please enable JavaScript on your browser.', 
      u'jsmath-requires':u' requires JavaScript to correctly process the mathematics on this page. ', 
      u'jsmath-warning':u'Warning: ', u'list-algorithm':u'List of Algorithms', 
      u'list-figure':u'List of Figures', u'list-table':u'List of Tables', 
      u'list-tableau':u'List of Tableaux', u'main-page':u'Main page', 
      u'next':u'Next', u'nomenclature':u'Nomenclature', 
      u'on-page':u' on page ', u'prev':u'Previous', 
      u'references':u'References', u'toc':u'Table of Contents', 
      u'toc-for':u'Contents for ', u'up':u'Up', 
      }

  languages = {
      u'american':u'en', u'british':u'en', u'deutsch':u'de', u'dutch':u'nl', 
      u'english':u'en', u'french':u'fr', u'ngerman':u'de', u'spanish':u'es', 
      }






class CommandLineParser(object):
  "A parser for runtime options"

  def __init__(self, options):
    self.options = options

  def parseoptions(self, args):
    "Parse command line options"
    if len(args) == 0:
      return None
    while len(args) > 0 and args[0].startswith('--'):
      key, value = self.readoption(args)
      if not key:
        return 'Option ' + value + ' not recognized'
      if not value:
        return 'Option ' + key + ' needs a value'
      setattr(self.options, key, value)
    return None

  def readoption(self, args):
    "Read the key and value for an option"
    arg = args[0][2:]
    del args[0]
    if '=' in arg:
      return self.readequals(arg, args)
    key = arg
    if not hasattr(self.options, key):
      return None, key
    current = getattr(self.options, key)
    if current.__class__ == bool:
      return key, True
    # read value
    if len(args) == 0:
      return key, None
    if args[0].startswith('"'):
      initial = args[0]
      del args[0]
      return key, self.readquoted(args, initial)
    value = args[0]
    del args[0]
    return key, value

  def readquoted(self, args, initial):
    "Read a value between quotes"
    value = initial[1:]
    while len(args) > 0 and not args[0].endswith('"') and not args[0].startswith('--'):
      value += ' ' + args[0]
      del args[0]
    if len(args) == 0 or args[0].startswith('--'):
      return None
    value += ' ' + args[0:-1]
    return value

  def readequals(self, arg, args):
    "Read a value with equals"
    split = arg.split('=', 1)
    key = split[0]
    if not hasattr(self.options, key):
      return None, key
    value = split[1]
    if not value.startswith('"'):
      return key, value
    return key, self.readquoted(args, value)



class Options(object):
  "A set of runtime options"

  instance = None

  location = None
  nocopy = False
  copyright = False
  debug = False
  quiet = False
  version = False
  hardversion = False
  versiondate = False
  html = False
  help = False
  showlines = True
  unicode = False
  iso885915 = False
  css = 'http://www.nongnu.org/elyxer/lyx.css'
  title = None
  directory = None
  destdirectory = None
  toc = False
  toctarget = ''
  forceformat = None
  lyxformat = False
  target = None
  splitpart = None
  memory = True
  lowmem = False
  nobib = False
  converter = 'imagemagick'
  raw = False
  jsmath = None
  mathjax = None
  nofooter = False
  template = None
  noconvert = False
  notoclabels = False
  letterfoot = True
  numberfoot = False
  symbolfoot = False
  hoverfoot = True
  marginfoot = False
  endfoot = False
  supfoot = True
  alignfoot = False
  footnotes = None

  branches = dict()

  def parseoptions(self, args):
    "Parse command line options"
    Options.location = args[0]
    del args[0]
    parser = CommandLineParser(Options)
    result = parser.parseoptions(args)
    if result:
      Trace.error(result)
      self.usage()
    if Options.help:
      self.usage()
    if Options.version:
      self.showversion()
    if Options.hardversion:
      self.showhardversion()
    if Options.versiondate:
      self.showversiondate()
    if Options.lyxformat:
      self.showlyxformat()
    if Options.splitpart:
      try:
        Options.splitpart = int(Options.splitpart)
        if Options.splitpart <= 0:
          Trace.error('--splitpart requires a number bigger than zero')
          self.usage()
      except:
        Trace.error('--splitpart needs a numeric argument, not ' + Options.splitpart)
        self.usage()
    if Options.lowmem or Options.toc:
      Options.memory = False
    self.parsefootnotes()
    # set in Trace if necessary
    for param in dir(Options):
      if hasattr(Trace, param + 'mode'):
        setattr(Trace, param + 'mode', getattr(self, param))

  def usage(self):
    "Show correct usage"
    Trace.error('Usage: ' + os.path.basename(Options.location) + ' [options] [filein] [fileout]')
    Trace.error('Convert LyX input file "filein" to HTML file "fileout".')
    Trace.error('If filein (or fileout) is not given use standard input (or output).')
    Trace.error('Main program of the eLyXer package (http://elyxer.nongnu.org/).')
    self.showoptions()

  def parsefootnotes(self):
    "Parse footnotes options."
    if not Options.footnotes:
      return
    Options.marginfoot = False
    Options.letterfoot = False
    options = Options.footnotes.split(',')
    for option in options:
      footoption = option + 'foot'
      if hasattr(Options, footoption):
        setattr(Options, footoption, True)
      else:
        Trace.error('Unknown footnotes option: ' + option)
    if not Options.endfoot and not Options.marginfoot and not Options.hoverfoot:
      Options.hoverfoot = True
    if not Options.numberfoot and not Options.symbolfoot:
      Options.letterfoot = True

  def showoptions(self):
    "Show all possible options"
    Trace.error('  Common options:')
    Trace.error('    --help:                 show this online help')
    Trace.error('    --quiet:                disables all runtime messages')
    Trace.error('')
    Trace.error('  Advanced options:')
    Trace.error('    --debug:                enable debugging messages (for developers)')
    Trace.error('    --version:              show version number and release date')
    Trace.error('    --lyxformat:            return the highest LyX version supported')
    Trace.error('  Options for HTML output:')
    Trace.error('    --title "title":        set the generated page title')
    Trace.error('    --css "file.css":       use a custom CSS file')
    Trace.error('    --html:                 output HTML 4.0 instead of the default XHTML')
    Trace.error('    --unicode:              full Unicode output')
    Trace.error('    --iso885915:            output a document with ISO-8859-15 encoding')
    Trace.error('    --nofooter:             remove the footer "create by eLyXer"')
    Trace.error('  Options for image output:')
    Trace.error('    --directory "img_dir":  look for images in the specified directory')
    Trace.error('    --destdirectory "dest": put converted images into this directory')
    Trace.error('    --forceformat ".ext":   force image output format')
    Trace.error('    --converter "inkscape": use an alternative program to convert images')
    Trace.error('    --noconvert:            do not convert images, use in their original format')
    Trace.error('  Options for footnote display:')
    Trace.error('    --numberfoot:           mark footnotes with numbers instead of letters')
    Trace.error('    --symbolfoot:           mark footnotes with symbols (*, **...)')
    Trace.error('    --hoverfoot:            show footnotes as hovering text (default)')
    Trace.error('    --marginfoot:           show footnotes with numbers instead of letters')
    Trace.error('    --endfoot:              show footnotes at the end of the page')
    Trace.error('    --supfoot:              use superscript for footnote markers (default)')
    Trace.error('    --alignfoot:            use aligned text for footnote markers')
    Trace.error('    --footnotes "options":  specify several comma-separated footnotes options')
    Trace.error('      Available options are: "number", "symbol", "hover", "margin", "end",')
    Trace.error('        "sup", "align"')
    Trace.error('  Advanced output options:')
    Trace.error('    --splitpart "depth":    split the resulting webpage at the given depth')
    Trace.error('    --toc:                  create a table of contents')
    Trace.error('    --target "frame":       make all links point to the given frame')
    Trace.error('    --toctarget "page":     generate a TOC that points to the given page')
    Trace.error('    --notoclabels:          omit the part labels in the TOC, such as Chapter')
    Trace.error('    --lowmem:               do the conversion on the fly (conserve memory)')
    Trace.error('    --raw:                  generate HTML without header or footer.')
    Trace.error('    --jsmath "URL":         use jsMath from the given URL to display equations')
    Trace.error('    --mathjax "URL":        use MathJax from the given URL to display equations')
    Trace.error('    --template "file":      use a template, put everything in <!--$content-->')
    Trace.error('    --copyright:            add a copyright notice at the bottom')
    Trace.error('    --nocopy (deprecated):  no effect, maintained for backwards compatibility')
    sys.exit()

  def showversion(self):
    "Return the current eLyXer version string"
    string = 'eLyXer version ' + GeneralConfig.version['number']
    string += ' (' + GeneralConfig.version['date'] + ')'
    Trace.error(string)
    sys.exit()

  def showhardversion(self):
    "Return just the version string"
    Trace.message(GeneralConfig.version['number'])
    sys.exit()

  def showversiondate(self):
    "Return just the version dte"
    Trace.message(GeneralConfig.version['date'])
    sys.exit()

  def showlyxformat(self):
    "Return just the lyxformat parameter"
    Trace.message(GeneralConfig.version['lyxformat'])
    sys.exit()

class BranchOptions(object):
  "A set of options for a branch"

  def __init__(self, name):
    self.name = name
    self.options = {'color':'#ffffff'}

  def set(self, key, value):
    "Set a branch option"
    if not key.startswith(ContainerConfig.string['startcommand']):
      Trace.error('Invalid branch option ' + key)
      return
    key = key.replace(ContainerConfig.string['startcommand'], '')
    self.options[key] = value

  def isselected(self):
    "Return if the branch is selected"
    if not 'selected' in self.options:
      return False
    return self.options['selected'] == '1'

  def __unicode__(self):
    "String representation"
    return 'options for ' + self.name + ': ' + unicode(self.options)



class Parser(object):
  "A generic parser"

  def __init__(self):
    self.begin = 0
    self.parameters = dict()

  def parseheader(self, reader):
    "Parse the header"
    header = reader.currentline().split()
    reader.nextline()
    self.begin = reader.linenumber
    return header

  def parseparameter(self, reader):
    "Parse a parameter"
    if reader.currentline().strip().startswith('<'):
      key, value = self.parsexml(reader)
      self.parameters[key] = value
      return
    split = reader.currentline().strip().split(' ', 1)
    reader.nextline()
    if len(split) == 0:
      return
    key = split[0]
    if len(split) == 1:
      self.parameters[key] = True
      return
    if not '"' in split[1]:
      self.parameters[key] = split[1].strip()
      return
    doublesplit = split[1].split('"')
    self.parameters[key] = doublesplit[1]

  def parsexml(self, reader):
    "Parse a parameter in xml form: <param attr1=value...>"
    strip = reader.currentline().strip()
    reader.nextline()
    if not strip.endswith('>'):
      Trace.error('XML parameter ' + strip + ' should be <...>')
    split = strip[1:-1].split()
    if len(split) == 0:
      Trace.error('Empty XML parameter <>')
      return None, None
    key = split[0]
    del split[0]
    if len(split) == 0:
      return key, dict()
    attrs = dict()
    for attr in split:
      if not '=' in attr:
        Trace.error('Erroneous attribute ' + attr)
        attr += '="0"'
      parts = attr.split('=')
      attrkey = parts[0]
      value = parts[1].split('"')[1]
      attrs[attrkey] = value
    return key, attrs

  def parseending(self, reader, process):
    "Parse until the current ending is found"
    if not self.ending:
      Trace.error('No ending for ' + unicode(self))
      return
    while not reader.currentline().startswith(self.ending):
      process()

  def parsecontainer(self, reader, contents):
    container = self.factory.createcontainer(reader)
    if container:
      container.parent = self.parent
      contents.append(container)

  def __unicode__(self):
    "Return a description"
    return self.__class__.__name__ + ' (' + unicode(self.begin) + ')'

class LoneCommand(Parser):
  "A parser for just one command line"

  def parse(self,reader):
    "Read nothing"
    return []

class TextParser(Parser):
  "A parser for a command and a bit of text"

  stack = []

  def __init__(self, container):
    Parser.__init__(self)
    self.ending = None
    if container.__class__.__name__ in ContainerConfig.endings:
      self.ending = ContainerConfig.endings[container.__class__.__name__]
    self.endings = []

  def parse(self, reader):
    "Parse lines as long as they are text"
    TextParser.stack.append(self.ending)
    self.endings = TextParser.stack + [ContainerConfig.endings['Layout'],
        ContainerConfig.endings['Inset'], self.ending]
    contents = []
    while not self.isending(reader):
      self.parsecontainer(reader, contents)
    return contents

  def isending(self, reader):
    "Check if text is ending"
    current = reader.currentline().split()
    if len(current) == 0:
      return False
    if current[0] in self.endings:
      if current[0] in TextParser.stack:
        TextParser.stack.remove(current[0])
      else:
        TextParser.stack = []
      return True
    return False

class ExcludingParser(Parser):
  "A parser that excludes the final line"

  def parse(self, reader):
    "Parse everything up to (and excluding) the final line"
    contents = []
    self.parseending(reader, lambda: self.parsecontainer(reader, contents))
    return contents

class BoundedParser(ExcludingParser):
  "A parser bound by a final line"

  def parse(self, reader):
    "Parse everything, including the final line"
    contents = ExcludingParser.parse(self, reader)
    # skip last line
    reader.nextline()
    return contents

class BoundedDummy(Parser):
  "A bound parser that ignores everything"

  def parse(self, reader):
    "Parse the contents of the container"
    self.parseending(reader, lambda: reader.nextline())
    # skip last line
    reader.nextline()
    return []

class StringParser(Parser):
  "Parses just a string"

  def parseheader(self, reader):
    "Do nothing, just take note"
    self.begin = reader.linenumber + 1
    return []

  def parse(self, reader):
    "Parse a single line"
    contents = reader.currentline()
    reader.nextline()
    return contents

class InsetParser(BoundedParser):
  "Parses a LyX inset"

  def parse(self, reader):
    "Parse inset parameters into a dictionary"
    startcommand = ContainerConfig.string['startcommand']
    while reader.currentline() != '' and not reader.currentline().startswith(startcommand):
      self.parseparameter(reader)
    return BoundedParser.parse(self, reader)






class ContainerOutput(object):
  "The generic HTML output for a container."

  def gethtml(self, container):
    "Show an error."
    Trace.error('gethtml() not implemented for ' + unicode(self))

  def isempty(self):
    "Decide if the output is empty: by default, not empty."
    return False

class EmptyOutput(ContainerOutput):

  def gethtml(self, container):
    "Return empty HTML code."
    return []

  def isempty(self):
    "This output is particularly empty."
    return True

class FixedOutput(ContainerOutput):
  "Fixed output"

  def gethtml(self, container):
    "Return constant HTML code"
    return container.html

class ContentsOutput(ContainerOutput):
  "Outputs the contents converted to HTML"

  def gethtml(self, container):
    "Return the HTML code"
    html = []
    if container.contents == None:
      return html
    for element in container.contents:
      if not hasattr(element, 'gethtml'):
        Trace.error('No html in ' + element.__class__.__name__ + ': ' + unicode(element))
        return html
      html += element.gethtml()
    return html

class TaggedOutput(ContentsOutput):
  "Outputs an HTML tag surrounding the contents."

  tag = None
  breaklines = False
  empty = False

  def settag(self, tag, breaklines=False, empty=False):
    "Set the value for the tag and other attributes."
    self.tag = tag
    if breaklines:
      self.breaklines = breaklines
    if empty:
      self.empty = empty
    return self

  def setbreaklines(self, breaklines):
    "Set the value for breaklines."
    self.breaklines = breaklines
    return self

  def gethtml(self, container):
    "Return the HTML code."
    if self.empty:
      return [self.selfclosing(container)]
    html = [self.open(container)]
    html += ContentsOutput.gethtml(self, container)
    html.append(self.close(container))
    return html

  def open(self, container):
    "Get opening line."
    if not self.checktag():
      return ''
    open = '<' + self.tag + '>'
    if self.breaklines:
      return open + '\n'
    return open

  def close(self, container):
    "Get closing line."
    if not self.checktag():
      return ''
    close = '</' + self.tag.split()[0] + '>'
    if self.breaklines:
      return '\n' + close + '\n'
    return close

  def selfclosing(self, container):
    "Get self-closing line."
    if not self.checktag():
      return ''
    selfclosing = '<' + self.tag + '/>'
    if self.breaklines:
      return selfclosing + '\n'
    return selfclosing

  def checktag(self):
    "Check that the tag is valid."
    if not self.tag:
      Trace.error('No tag in ' + unicode(container))
      return False
    if self.tag == '':
      return False
    return True

class StringOutput(ContainerOutput):
  "Returns a bare string as output"

  def gethtml(self, container):
    "Return a bare string"
    return [container.string]







import sys
import codecs


class LineReader(object):
  "Reads a file line by line"

  def __init__(self, filename):
    if isinstance(filename, file):
      self.file = filename
    else:
      self.file = codecs.open(filename, 'rU', 'utf-8')
    self.linenumber = 1
    self.lastline = None
    self.current = None
    self.mustread = True
    self.depleted = False
    try:
      self.readline()
    except UnicodeDecodeError:
      # try compressed file
      import gzip
      self.file = gzip.open(filename, 'rb')
      self.readline()

  def setstart(self, firstline):
    "Set the first line to read."
    for i in range(firstline):
      self.file.readline()
    self.linenumber = firstline

  def setend(self, lastline):
    "Set the last line to read."
    self.lastline = lastline

  def currentline(self):
    "Get the current line"
    if self.mustread:
      self.readline()
    return self.current

  def nextline(self):
    "Go to next line"
    if self.depleted:
      Trace.fatal('Read beyond file end')
    self.mustread = True

  def readline(self):
    "Read a line from file"
    self.current = self.file.readline()
    if not isinstance(self.file, codecs.StreamReaderWriter):
      self.current = self.current.decode('utf-8')
    if len(self.current) == 0:
      self.depleted = True
    self.current = self.current.rstrip('\n\r')
    self.linenumber += 1
    self.mustread = False
    Trace.prefix = 'Line ' + unicode(self.linenumber) + ': '
    if self.linenumber % 1000 == 0:
      Trace.message('Parsing')

  def finished(self):
    "Find out if the file is finished"
    if self.lastline and self.linenumber == self.lastline:
      return True
    if self.mustread:
      self.readline()
    return self.depleted

  def close(self):
    self.file.close()

class LineWriter(object):
  "Writes a file as a series of lists"

  def __init__(self, filename):
    if isinstance(filename, file):
      self.file = filename
      self.filename = None
    else:
      self.file = codecs.open(filename, 'w', "utf-8")
      self.filename = filename

  def write(self, strings):
    "Write a list of strings"
    for string in strings:
      if not isinstance(string, basestring):
        Trace.error('Not a string: ' + unicode(string) + ' in ' + unicode(strings))
        return
      self.writestring(string)

  def writestring(self, string):
    "Write a string"
    if self.file == sys.stdout:
      string = string.encode('utf-8')
    self.file.write(string)

  def writeline(self, line):
    "Write a line to file"
    self.writestring(line + '\n')

  def close(self):
    self.file.close()



class Position(object):
  "A position in a text to parse"

  def __init__(self):
    self.endinglist = EndingList()

  def checkbytemark(self):
    "Check for a Unicode byte mark and skip it."
    if self.finished():
      return
    if ord(self.current()) == 0xfeff:
      self.skipcurrent()

  def skip(self, string):
    "Skip a string"
    Trace.error('Unimplemented skip()')

  def identifier(self):
    "Return an identifier for the current position."
    Trace.error('Unimplemented identifier()')
    return 'Error'

  def isout(self):
    "Find out if we are out of the position yet."
    Trace.error('Unimplemented isout()')
    return True

  def current(self):
    "Return the current character"
    Trace.error('Unimplemented current()')
    return ''

  def extract(self, length):
    "Extract the next string of the given length, or None if not enough text."
    Trace.error('Unimplemented extract()')
    return None

  def checkfor(self, string):
    "Check for a string at the given position."
    return string == self.extract(len(string))

  def checkforlower(self, string):
    "Check for a string in lower case."
    extracted = self.extract(len(string))
    if not extracted:
      return False
    return string.lower() == self.extract(len(string)).lower()

  def finished(self):
    "Find out if the current formula has finished"
    if self.isout():
      self.endinglist.checkpending()
      return True
    return self.endinglist.checkin(self)

  def skipcurrent(self):
    "Return the current character and skip it."
    current = self.current()
    self.skip(current)
    return current

  def next(self):
    "Advance the position and return the next character."
    self.skipcurrent()
    return self.current()

  def checkskip(self, string):
    "Check for a string at the given position; if there, skip it"
    if not self.checkfor(string):
      return False
    self.skip(string)
    return True

  def glob(self, currentcheck):
    "Glob a bit of text that satisfies a check"
    glob = ''
    while not self.finished() and currentcheck(self.current()):
      glob += self.current()
      self.skip(self.current())
    return glob

  def globalpha(self):
    "Glob a bit of alpha text"
    return self.glob(lambda current: current.isalpha())

  def globnumber(self):
    "Glob a row of digits."
    return self.glob(lambda current: current.isdigit())

  def checkidentifier(self):
    "Check if the current character belongs to an identifier."
    return self.isidentifier(self.current())

  def isidentifier(self, char):
    "Return if the given character is alphanumeric or _."
    if char.isalnum() or char == '_':
      return True
    return False

  def globidentifier(self):
    "Glob alphanumeric and _ symbols."
    return self.glob(lambda current: self.isidentifier(current))

  def skipspace(self):
    "Skip all whitespace at current position"
    return self.glob(lambda current: current.isspace())

  def globincluding(self, magicchar):
    "Glob a bit of text up to (including) the magic char."
    glob = self.glob(lambda current: current != magicchar) + magicchar
    self.skip(magicchar)
    return glob

  def globexcluding(self, magicchar):
    "Glob a bit of text up until (excluding) the magic char."
    return self.glob(lambda current: current != magicchar)

  def pushending(self, ending, optional = False):
    "Push a new ending to the bottom"
    self.endinglist.add(ending, optional)

  def popending(self, expected = None):
    "Pop the ending found at the current position"
    ending = self.endinglist.pop(self)
    if expected and expected != ending:
      Trace.error('Expected ending ' + expected + ', got ' + ending)
    self.skip(ending)
    return ending

class TextPosition(Position):
  "A parse position based on a raw text."

  def __init__(self, text):
    "Create the position from some text."
    Position.__init__(self)
    self.pos = 0
    self.text = text
    self.checkbytemark()

  def skip(self, string):
    "Skip a string of characters."
    self.pos += len(string)

  def identifier(self):
    "Return a sample of the remaining text."
    length = 30
    if self.pos + length > len(self.text):
      length = len(self.text) - self.pos - 1
    return '*' + self.text[self.pos:self.pos + length]

  def isout(self):
    "Find out if we are out of the text yet."
    return self.pos >= len(self.text)

  def current(self):
    "Return the current character, assuming we are not out."
    return self.text[self.pos]

  def extract(self, length):
    "Extract the next string of the given length, or None if not enough text."
    if self.pos + length > len(self.text):
      return None
    return self.text[self.pos : self.pos + length]

class FilePosition(Position):
  "A parse position based on an underlying file."

  def __init__(self, filename):
    "Create the position from a file."
    Position.__init__(self)
    self.reader = LineReader(filename)
    self.number = 1
    self.pos = 0
    self.checkbytemark()

  def skip(self, string):
    "Skip a string of characters."
    length = len(string)
    while self.pos + length > len(self.reader.currentline()):
      length -= len(self.reader.currentline()) - self.pos + 1
      self.nextline()
    self.pos += length

  def nextline(self):
    "Go to the next line."
    self.reader.nextline()
    self.number += 1
    self.pos = 0

  def identifier(self):
    "Return the current line and line number in the file."
    before = self.reader.currentline()[:self.pos - 1]
    after = self.reader.currentline()[self.pos:]
    return 'line ' + unicode(self.number) + ': ' + before + '*' + after

  def isout(self):
    "Find out if we are out of the text yet."
    if self.pos > len(self.reader.currentline()):
      if self.pos > len(self.reader.currentline()) + 1:
        Trace.error('Out of the line ' + self.reader.currentline() + ': ' + unicode(self.pos))
      self.nextline()
    return self.reader.finished()

  def current(self):
    "Return the current character, assuming we are not out."
    if self.pos == len(self.reader.currentline()):
      return '\n'
    if self.pos > len(self.reader.currentline()):
      Trace.error('Out of the line ' + self.reader.currentline() + ': ' + unicode(self.pos))
      return '*'
    return self.reader.currentline()[self.pos]

  def extract(self, length):
    "Extract the next string of the given length, or None if not enough text."
    if self.pos + length > len(self.reader.currentline()):
      return None
    return self.reader.currentline()[self.pos : self.pos + length]

class EndingList(object):
  "A list of position endings"

  def __init__(self):
    self.endings = []

  def add(self, ending, optional):
    "Add a new ending to the list"
    self.endings.append(PositionEnding(ending, optional))

  def checkin(self, pos):
    "Search for an ending"
    if self.findending(pos):
      return True
    return False

  def pop(self, pos):
    "Remove the ending at the current position"
    if pos.isout():
      Trace.error('No ending out of bounds')
      return ''
    ending = self.findending(pos)
    if not ending:
      Trace.error('No ending at ' + pos.current())
      return ''
    for each in reversed(self.endings):
      self.endings.remove(each)
      if each == ending:
        return each.ending
      elif not each.optional:
        Trace.error('Removed non-optional ending ' + each)
    Trace.error('No endings left')
    return ''

  def findending(self, pos):
    "Find the ending at the current position"
    if len(self.endings) == 0:
      return None
    for index, ending in enumerate(reversed(self.endings)):
      if ending.checkin(pos):
        return ending
      if not ending.optional:
        return None
    return None

  def checkpending(self):
    "Check if there are any pending endings"
    if len(self.endings) != 0:
      Trace.error('Pending ' + unicode(self) + ' left open')

  def __unicode__(self):
    "Printable representation"
    string = 'endings ['
    for ending in self.endings:
      string += unicode(ending) + ','
    if len(self.endings) > 0:
      string = string[:-1]
    return string + ']'

class PositionEnding(object):
  "An ending for a parsing position"

  def __init__(self, ending, optional):
    self.ending = ending
    self.optional = optional

  def checkin(self, pos):
    "Check for the ending"
    return pos.checkfor(self.ending)

  def __unicode__(self):
    "Printable representation"
    string = 'Ending ' + self.ending
    if self.optional:
      string += ' (optional)'
    return string



class Container(object):
  "A container for text and objects in a lyx file"

  partkey = None
  parent = None
  begin = None

  def __init__(self):
    self.contents = list()

  def process(self):
    "Process contents"
    pass

  def gethtml(self):
    "Get the resulting HTML"
    html = self.output.gethtml(self)
    if isinstance(html, basestring):
      Trace.error('Raw string ' + html)
      html = [html]
    return self.escapeall(html)

  def escapeall(self, lines):
    "Escape all lines in an array according to the output options."
    result = []
    for line in lines:
      if Options.html:
        line = self.escape(line, EscapeConfig.html)
      if Options.iso885915:
        line = self.escape(line, EscapeConfig.iso885915)
        line = self.escapeentities(line)
      elif not Options.unicode:
        line = self.escape(line, EscapeConfig.nonunicode)
      result.append(line)
    return result

  def escape(self, line, replacements = EscapeConfig.entities):
    "Escape a line with replacements from a map"
    pieces = replacements.keys()
    # do them in order
    pieces.sort()
    for piece in pieces:
      if piece in line:
        line = line.replace(piece, replacements[piece])
    return line

  def escapeentities(self, line):
    "Escape all Unicode characters to HTML entities."
    result = ''
    pos = TextPosition(line)
    while not pos.finished():
      if ord(pos.current()) > 128:
        codepoint = hex(ord(pos.current()))
        if codepoint == '0xd835':
          codepoint = hex(ord(pos.next()) + 0xf800)
        result += '&#' + codepoint[1:] + ';'
      else:
        result += pos.current()
      pos.skipcurrent()
    return result

  def searchall(self, type):
    "Search for all embedded containers of a given type"
    list = []
    self.searchprocess(type, lambda container: list.append(container))
    return list

  def searchremove(self, type):
    "Search for all containers of a type and remove them"
    list = self.searchall(type)
    for container in list:
      container.parent.contents.remove(container)
    return list

  def searchprocess(self, type, process):
    "Search for elements of a given type and process them"
    self.locateprocess(lambda container: isinstance(container, type), process)

  def locateprocess(self, locate, process):
    "Search for all embedded containers and process them"
    for container in self.contents:
      container.locateprocess(locate, process)
      if locate(container):
        process(container)

  def recursivesearch(self, locate, recursive, process):
    "Perform a recursive search in the container."
    for container in self.contents:
      if recursive(container):
        container.recursivesearch(locate, recursive, process)
      if locate(container):
        process(container)

  def extracttext(self):
    "Extract all text from allowed containers."
    result = ''
    constants = ContainerExtractor(ContainerConfig.extracttext).extract(self)
    for constant in constants:
      result += constant.string
    return result

  def group(self, index, group, isingroup):
    "Group some adjoining elements into a group"
    if index >= len(self.contents):
      return
    if hasattr(self.contents[index], 'grouped'):
      return
    while index < len(self.contents) and isingroup(self.contents[index]):
      self.contents[index].grouped = True
      group.contents.append(self.contents[index])
      self.contents.pop(index)
    self.contents.insert(index, group)

  def remove(self, index):
    "Remove a container but leave its contents"
    container = self.contents[index]
    self.contents.pop(index)
    while len(container.contents) > 0:
      self.contents.insert(index, container.contents.pop())

  def tree(self, level = 0):
    "Show in a tree"
    Trace.debug("  " * level + unicode(self))
    for container in self.contents:
      container.tree(level + 1)

  def getparameter(self, name):
    "Get the value of a parameter, if present."
    if not name in self.parameters:
      return None
    return self.parameters[name]

  def getparameterlist(self, name):
    "Get the value of a comma-separated parameter as a list."
    paramtext = self.getparameter(name)
    if not paramtext:
      return []
    return paramtext.split(',')

  def hasemptyoutput(self):
    "Check if the parent's output is empty."
    current = self.parent
    while current:
      if current.output.isempty():
        return True
      current = current.parent
    return False

  def __unicode__(self):
    "Get a description"
    if not self.begin:
      return self.__class__.__name__
    return self.__class__.__name__ + '@' + unicode(self.begin)

class BlackBox(Container):
  "A container that does not output anything"

  def __init__(self):
    self.parser = LoneCommand()
    self.output = EmptyOutput()
    self.contents = []

class LyXFormat(BlackBox):
  "Read the lyxformat command"

  def process(self):
    "Show warning if version < 276"
    version = int(self.header[1])
    if version < 276:
      Trace.error('Warning: unsupported old format version ' + str(version))
    if version > int(GeneralConfig.version['lyxformat']):
      Trace.error('Warning: unsupported new format version ' + str(version))

class StringContainer(Container):
  "A container for a single string"

  parsed = None

  def __init__(self):
    self.parser = StringParser()
    self.output = StringOutput()
    self.string = ''

  def process(self):
    "Replace special chars from the contents."
    if self.parsed:
      self.string = self.replacespecial(self.parsed)
      self.parsed = None

  def replacespecial(self, line):
    "Replace all special chars from a line"
    replaced = self.escape(line, EscapeConfig.entities)
    replaced = self.changeline(replaced)
    if ContainerConfig.string['startcommand'] in replaced and len(replaced) > 1:
      # unprocessed commands
      if self.begin:
        message = 'Unknown command at ' + unicode(self.begin) + ': '
      else:
        message = 'Unknown command: '
      Trace.error(message + replaced.strip())
    return replaced

  def changeline(self, line):
    line = self.escape(line, EscapeConfig.chars)
    if not ContainerConfig.string['startcommand'] in line:
      return line
    line = self.escape(line, EscapeConfig.commands)
    return line

  def extracttext(self):
    "Return all text."
    return self.string
  
  def __unicode__(self):
    "Return a printable representation."
    result = 'StringContainer'
    if self.begin:
      result += '@' + unicode(self.begin)
    ellipsis = '...'
    if len(self.string.strip()) <= 15:
      ellipsis = ''
    return result + ' (' + self.string.strip()[:15] + ellipsis + ')'

class Constant(StringContainer):
  "A constant string"

  def __init__(self, text):
    self.contents = []
    self.string = text
    self.output = StringOutput()

  def __unicode__(self):
    return 'Constant: ' + self.string

class TaggedText(Container):
  "Text inside a tag"

  output = None

  def __init__(self):
    self.parser = TextParser(self)
    self.output = TaggedOutput()

  def complete(self, contents, tag, breaklines=False):
    "Complete the tagged text and return it"
    self.contents = contents
    self.output.tag = tag
    self.output.breaklines = breaklines
    return self

  def constant(self, text, tag, breaklines=False):
    "Complete the tagged text with a constant"
    constant = Constant(text)
    return self.complete([constant], tag, breaklines)

  def __unicode__(self):
    "Return a printable representation."
    if not hasattr(self.output, 'tag'):
      return 'Emtpy tagged text'
    if not self.output.tag:
      return 'Tagged <unknown tag>'
    return 'Tagged <' + self.output.tag + '>'






class FormulaParser(Parser):
  "Parses a formula"

  def parseheader(self, reader):
    "See if the formula is inlined"
    self.begin = reader.linenumber + 1
    if reader.currentline().find(FormulaConfig.starts['simple']) > 0:
      return ['inline']
    if reader.currentline().find(FormulaConfig.starts['complex']) > 0:
      return ['block']
    if reader.currentline().find(FormulaConfig.starts['unnumbered']) > 0:
      return ['block']
    return ['numbered']
  
  def parse(self, reader):
    "Parse the formula until the end"
    formula = self.parseformula(reader)
    while not reader.currentline().startswith(self.ending):
      stripped = reader.currentline().strip()
      if len(stripped) > 0:
        Trace.error('Unparsed formula line ' + stripped)
      reader.nextline()
    reader.nextline()
    return formula

  def parseformula(self, reader):
    "Parse the formula contents"
    simple = FormulaConfig.starts['simple']
    if simple in reader.currentline():
      rest = reader.currentline().split(simple, 1)[1]
      if simple in rest:
        # formula is $...$
        return self.parsesingleliner(reader, simple, simple)
      # formula is multiline $...$
      return self.parsemultiliner(reader, simple, simple)
    if FormulaConfig.starts['complex'] in reader.currentline():
      # formula of the form \[...\]
      return self.parsemultiliner(reader, FormulaConfig.starts['complex'],
          FormulaConfig.endings['complex'])
    beginbefore = FormulaConfig.starts['beginbefore']
    beginafter = FormulaConfig.starts['beginafter']
    if beginbefore in reader.currentline():
      if reader.currentline().strip().endswith(beginafter):
        current = reader.currentline().strip()
        endsplit = current.split(beginbefore)[1].split(beginafter)
        startpiece = beginbefore + endsplit[0] + beginafter
        endbefore = FormulaConfig.endings['endbefore']
        endafter = FormulaConfig.endings['endafter']
        endpiece = endbefore + endsplit[0] + endafter
        return startpiece + self.parsemultiliner(reader, startpiece, endpiece) + endpiece
      Trace.error('Missing ' + beginafter + ' in ' + reader.currentline())
      return ''
    begincommand = FormulaConfig.starts['command']
    beginbracket = FormulaConfig.starts['bracket']
    if begincommand in reader.currentline() and beginbracket in reader.currentline():
      endbracket = FormulaConfig.endings['bracket']
      return self.parsemultiliner(reader, beginbracket, endbracket)
    Trace.error('Formula beginning ' + reader.currentline() + ' is unknown')
    return ''

  def parsesingleliner(self, reader, start, ending):
    "Parse a formula in one line"
    line = reader.currentline().strip()
    if not start in line:
      Trace.error('Line ' + line + ' does not contain formula start ' + start)
      return ''
    if not line.endswith(ending):
      Trace.error('Formula ' + line + ' does not end with ' + ending)
      return ''
    index = line.index(start)
    rest = line[index + len(start):-len(ending)]
    reader.nextline()
    return rest

  def parsemultiliner(self, reader, start, ending):
    "Parse a formula in multiple lines"
    formula = ''
    line = reader.currentline()
    if not start in line:
      Trace.error('Line ' + line.strip() + ' does not contain formula start ' + start)
      return ''
    index = line.index(start)
    line = line[index + len(start):].strip()
    while not line.endswith(ending):
      formula += line + '\n'
      reader.nextline()
      line = reader.currentline()
    formula += line[:-len(ending)]
    reader.nextline()
    return formula

class MacroParser(FormulaParser):
  "A parser for a formula macro."

  def parseheader(self, reader):
    "See if the formula is inlined"
    self.begin = reader.linenumber + 1
    return ['inline']
  
  def parse(self, reader):
    "Parse the formula until the end"
    formula = self.parsemultiliner(reader, self.parent.start, self.ending)
    reader.nextline()
    return formula
  








class FormulaBit(Container):
  "A bit of a formula"

  def __init__(self):
    # type can be 'alpha', 'number', 'font'
    self.type = None
    self.original = ''
    self.contents = []
    self.output = ContentsOutput()

  def setfactory(self, factory):
    "Set the internal formula factory."
    self.factory = factory
    return self

  def add(self, bit):
    "Add any kind of formula bit already processed"
    self.contents.append(bit)
    self.original += bit.original
    bit.parent = self

  def skiporiginal(self, string, pos):
    "Skip a string and add it to the original formula"
    self.original += string
    if not pos.checkskip(string):
      Trace.error('String ' + string + ' not at ' + pos.identifier())

  def clone(self):
    "Return a copy of itself."
    return self.factory.parseformula(self.original)

  def __unicode__(self):
    "Get a string representation"
    return self.__class__.__name__ + ' read in ' + self.original

class TaggedBit(FormulaBit):
  "A tagged string in a formula"

  def constant(self, constant, tag):
    "Set the constant and the tag"
    self.output = TaggedOutput().settag(tag)
    self.add(FormulaConstant(constant))
    return self

  def complete(self, contents, tag):
    "Set the constant and the tag"
    self.contents = contents
    self.output = TaggedOutput().settag(tag)
    return self

class FormulaConstant(Constant):
  "A constant string in a formula"

  def __init__(self, string):
    "Set the constant string"
    Constant.__init__(self, string)
    self.original = string
    self.type = None

  def clone(self):
    "Return a copy of itself."
    return FormulaConstant(self.original)

  def __unicode__(self):
    "Return a printable representation."
    return 'Formula constant: ' + self.string

class RawText(FormulaBit):
  "A bit of text inside a formula"

  def detect(self, pos):
    "Detect a bit of raw text"
    return pos.current().isalpha()

  def parsebit(self, pos):
    "Parse alphabetic text"
    alpha = pos.globalpha()
    self.add(FormulaConstant(alpha))
    self.type = 'alpha'

class FormulaSymbol(FormulaBit):
  "A symbol inside a formula"

  modified = FormulaConfig.modified
  unmodified = FormulaConfig.unmodified['characters']

  def detect(self, pos):
    "Detect a symbol"
    if pos.current() in FormulaSymbol.unmodified:
      return True
    if pos.current() in FormulaSymbol.modified:
      return True
    return False

  def parsebit(self, pos):
    "Parse the symbol"
    if pos.current() in FormulaSymbol.unmodified:
      self.addsymbol(pos.current(), pos)
      return
    if pos.current() in FormulaSymbol.modified:
      self.addsymbol(FormulaSymbol.modified[pos.current()], pos)
      return
    Trace.error('Symbol ' + pos.current() + ' not found')

  def addsymbol(self, symbol, pos):
    "Add a symbol"
    self.skiporiginal(pos.current(), pos)
    self.contents.append(FormulaConstant(symbol))

class FormulaNumber(FormulaBit):
  "A string of digits in a formula"

  def detect(self, pos):
    "Detect a digit"
    return pos.current().isdigit()

  def parsebit(self, pos):
    "Parse a bunch of digits"
    digits = pos.glob(lambda current: current.isdigit())
    self.add(FormulaConstant(digits))
    self.type = 'number'

class Comment(FormulaBit):
  "A LaTeX comment: % to the end of the line."

  start = FormulaConfig.starts['comment']

  def detect(self, pos):
    "Detect the %."
    return pos.current() == self.start

  def parsebit(self, pos):
    "Parse to the end of the line."
    self.original += pos.globincluding('\n')

class WhiteSpace(FormulaBit):
  "Some white space inside a formula."

  def detect(self, pos):
    "Detect the white space."
    return pos.current().isspace()

  def parsebit(self, pos):
    "Parse all whitespace."
    self.original += pos.skipspace()

class Bracket(FormulaBit):
  "A {} bracket inside a formula"

  start = FormulaConfig.starts['bracket']
  ending = FormulaConfig.endings['bracket']

  def __init__(self):
    "Create a (possibly literal) new bracket"
    FormulaBit.__init__(self)
    self.inner = None

  def detect(self, pos):
    "Detect the start of a bracket"
    return pos.checkfor(self.start)

  def parsebit(self, pos):
    "Parse the bracket"
    self.parsecomplete(pos, self.innerformula)
    return self

  def parsetext(self, pos):
    "Parse a text bracket"
    self.parsecomplete(pos, self.innertext)
    return self

  def parseliteral(self, pos):
    "Parse a literal bracket"
    self.parsecomplete(pos, self.innerliteral)
    return self

  def parsecomplete(self, pos, innerparser):
    "Parse the start and end marks"
    if not pos.checkfor(self.start):
      Trace.error('Bracket should start with ' + self.start + ' at ' + pos.identifier())
      return None
    self.skiporiginal(self.start, pos)
    pos.pushending(self.ending)
    innerparser(pos)
    self.original += pos.popending(self.ending)

  def innerformula(self, pos):
    "Parse a whole formula inside the bracket"
    while self.factory.detectany(pos):
      self.add(self.factory.parseany(pos))
    if pos.finished():
      return
    if pos.current() != self.ending:
      Trace.error('No formula in bracket at ' + pos.identifier())
    return

  def innertext(self, pos):
    "Parse some text inside the bracket, following textual rules."
    specialchars = FormulaConfig.symbolfunctions.keys()
    specialchars.append(FormulaConfig.starts['command'])
    specialchars.append(FormulaConfig.starts['bracket'])
    specialchars.append(Comment.start)
    while not pos.finished():
      if pos.current() in specialchars:
        if self.factory.detectany(pos):
          self.add(self.factory.parseany(pos))
          pos.checkskip(' ')
      else:
        self.add(FormulaConstant(pos.skipcurrent()))

  def innerliteral(self, pos):
    "Parse a literal inside the bracket, which cannot generate html"
    self.literal = ''
    while not pos.current() == self.ending:
      if pos.current() == self.start:
        self.parseliteral(pos)
      else:
        self.literal += pos.skipcurrent()
    self.original += self.literal

class SquareBracket(Bracket):
  "A [] bracket inside a formula"

  start = FormulaConfig.starts['squarebracket']
  ending = FormulaConfig.endings['squarebracket']




class FormulaProcessor(object):
  "A processor specifically for formulas."

  def process(self, bit):
    "Process the contents of every formula bit, recursively."
    self.processcontents(bit)
    self.processlimits(bit)
    self.traversewhole(bit)

  def processcontents(self, bit):
    "Process the contents of a formula bit."
    if not isinstance(bit, FormulaBit):
      return
    bit.process()
    for element in bit.contents:
      self.processcontents(element)

  def processlimits(self, bit):
    "Process any limits in a formula bit."
    if not isinstance(bit, FormulaBit):
      return
    for index, element in enumerate(bit.contents):
      self.checklimited(bit.contents, index)
      self.processlimits(element)

  def checklimited(self, contents, index):
    "Check for a command with limits"
    bit = contents[index]
    if not hasattr(bit, 'command'):
      return
    if not bit.command in FormulaConfig.limits['commands']:
      return
    limits = self.findlimits(contents, index + 1)
    limits.reverse()
    if len(limits) == 0:
      return
    tagged = TaggedBit().complete(limits, 'span class="limits"')
    contents.insert(index + 1, tagged)

  def findlimits(self, contents, index):
    "Find the limits for the command"
    limits = []
    while index < len(contents):
      if not self.checklimits(contents, index):
        return limits
      limits.append(contents[index])
      del contents[index]
    return limits

  def checklimits(self, contents, index):
    "Check for a command making the limits"
    bit = contents[index]
    if not hasattr(bit, 'command'):
      return
    if not bit.command in FormulaConfig.limits['operands']:
      return False
    bit.output.tag += ' class="bigsymbol"'
    return True

  def traversewhole(self, formula):
    "Traverse over the contents to alter variables and space units."
    last = None
    for bit, contents in self.traverse(formula):
      if bit.type == 'alpha':
        self.italicize(bit, contents)
      elif bit.type == 'font' and last and last.type == 'number':
        bit.contents.insert(0, FormulaConstant(u' '))
      last = bit

  def traverse(self, bit):
    "Traverse a formula and yield a flattened structure of (bit, list) pairs."
    for element in bit.contents:
      if hasattr(element, 'type') and element.type:
        yield (element, bit.contents)
      elif isinstance(element, FormulaBit):
        for pair in self.traverse(element):
          yield pair

  def italicize(self, bit, contents):
    "Italicize the given bit of text."
    index = contents.index(bit)
    contents[index] = TaggedBit().complete([bit], 'i')




class Formula(Container):
  "A LaTeX formula"

  def __init__(self):
    self.parser = FormulaParser()
    self.output = TaggedOutput().settag('span class="formula"')

  def process(self):
    "Convert the formula to tags"
    if self.header[0] != 'inline':
      self.output.settag('div class="formula"', True)
    if Options.jsmath:
      if self.header[0] != 'inline':
        self.output = TaggedOutput().settag('div class="math"')
      else:
        self.output = TaggedOutput().settag('span class="math"')
      self.contents = [Constant(self.parsed)]
      return
    if Options.mathjax:
      self.output.tag = 'span class="MathJax_Preview"'
      tag = 'script type="math/tex'
      if self.header[0] != 'inline':
        tag += ';mode=display'
      self.contents = [TaggedText().constant(self.parsed, tag + '"', True)]
      return
    whole = FormulaFactory().parseformula(self.parsed)
    FormulaProcessor().process(whole)
    whole.parent = self
    self.contents = [whole]

  def __unicode__(self):
    "Return a printable representation."
    if self.partkey and self.partkey.number:
      return 'Formula (' + self.partkey.number + ')'
    return 'Unnumbered formula'

class WholeFormula(FormulaBit):
  "Parse a whole formula"

  def detect(self, pos):
    "Check in the factory"
    return self.factory.detectany(pos)

  def parsebit(self, pos):
    "Parse with any formula bit"
    while self.factory.detectany(pos):
      bit = self.factory.parseany(pos)
      #Trace.debug(bit.original + ' -> ' + unicode(bit.gethtml()))
      self.add(bit)

class FormulaFactory(object):
  "Construct bits of formula"

  # bit types will be appended later
  types = [FormulaSymbol, RawText, FormulaNumber, Bracket]
  ignoredtypes = [Comment, WhiteSpace]
  defining = False

  def __init__(self):
    "Initialize the map of instances."
    self.instances = dict()

  def detectany(self, pos):
    "Detect if there is a next bit"
    if pos.finished():
      return False
    for type in FormulaFactory.types:
      if self.detecttype(type, pos):
        return True
    return False

  def detecttype(self, type, pos):
    "Detect a bit of a given type."
    self.clearignored(pos)
    if pos.finished():
      return False
    return self.instance(type).detect(pos)

  def instance(self, type):
    "Get an instance of the given type."
    if not type in self.instances or not self.instances[type]:
      self.instances[type] = self.create(type)
    return self.instances[type]

  def create(self, type):
    "Create a new formula bit of the given type."
    return Cloner.create(type).setfactory(self)

  def clearignored(self, pos):
    "Clear all ignored types."
    while not pos.finished():
      if not self.clearany(pos):
        return

  def clearany(self, pos):
    "Cleary any ignored type."
    for type in self.ignoredtypes:
      if self.instance(type).detect(pos):
        self.parsetype(type, pos)
        return True
    return False

  def parseany(self, pos):
    "Parse any formula bit at the current location."
    for type in FormulaFactory.types:
      if self.detecttype(type, pos):
        return self.parsetype(type, pos)
    Trace.error('Unrecognized formula at ' + pos.identifier())
    return FormulaConstant(pos.skipcurrent())

  def parsetype(self, type, pos):
    "Parse the given type and return it."
    bit = self.instance(type)
    self.instances[type] = None
    returnedbit = bit.parsebit(pos)
    if returnedbit:
      return returnedbit.setfactory(self)
    return bit

  def parseformula(self, formula):
    "Parse a string of text that contains a whole formula."
    pos = TextPosition(formula)
    whole = self.create(WholeFormula)
    if whole.detect(pos):
      whole.parsebit(pos)
      return whole
    # no formula found
    if not pos.finished():
      Trace.error('Unknown formula at: ' + pos.identifier())
      whole.add(TaggedBit().constant(formula, 'span class="unknown"'))
    return whole




import unicodedata












import gettext





class DocumentParameters(object):
  "Global parameters for the document."

  pdftitle = None
  indentstandard = False
  tocdepth = 10
  startinglevel = 0
  maxdepth = 10
  language = None
  bibliography = None
  outputchanges = False



class Translator(object):
  "Reads the configuration file and tries to find a translation."
  "Otherwise falls back to the messages in the config file."

  instance = None

  def translate(cls, key):
    "Get the translated message for a key."
    return cls.instance.getmessage(key)

  translate = classmethod(translate)

  def __init__(self):
    self.translation = None
    self.first = True

  def findtranslation(self):
    "Find the translation for the document language."
    self.langcodes = None
    if not DocumentParameters.language:
      Trace.error('No language in document')
      return
    if not DocumentParameters.language in TranslationConfig.languages:
      Trace.error('Unknown language ' + DocumentParameters.language)
      return
    if TranslationConfig.languages[DocumentParameters.language] == 'en':
      return
    langcodes = [TranslationConfig.languages[DocumentParameters.language]]
    try:
      self.translation = gettext.translation('elyxer', None, langcodes)
    except IOError:
      Trace.error('No translation for ' + unicode(langcodes))

  def getmessage(self, key):
    "Get the translated message for the given key."
    if self.first:
      self.findtranslation()
      self.first = False
    message = self.getuntranslated(key)
    if not self.translation:
      return message
    try:
      message = self.translation.ugettext(message)
    except IOError:
      pass
    return message

  def getuntranslated(self, key):
    "Get the untranslated message."
    if not key in TranslationConfig.constants:
      Trace.error('Cannot translate ' + key)
      return key
    return TranslationConfig.constants[key]

Translator.instance = Translator()



class NumberCounter(object):
  "A counter for numbers (by default)."
  "The type can be changed to return letters, roman numbers..."

  name = None
  value = None
  mode = None
  master = None

  letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  symbols = NumberingConfig.sequence['symbols']
  romannumerals = [
      ('M', 1000), ('CM', 900), ('D', 500), ('CD', 400), ('C', 100),
      ('XC', 90), ('L', 50), ('XL', 40), ('X', 10), ('IX', 9), ('V', 5),
      ('IV', 4), ('I', 1)
      ]

  def __init__(self, name):
    "Give a name to the counter."
    self.name = name

  def setmode(self, mode):
    "Set the counter mode. Can be changed at runtime."
    self.mode = mode
    return self

  def init(self, value):
    "Set an initial value."
    self.value = value

  def increase(self):
    "Increase the counter value and return the counter."
    if not self.value:
      self.value = 0
    self.value += 1
    return self

  def gettext(self):
    "Get the next value as a text string."
    return unicode(self.value)

  def getletter(self):
    "Get the next value as a letter."
    return self.getsequence(self.letters)

  def getsymbol(self):
    "Get the next value as a symbol."
    return self.getsequence(self.symbols)

  def getsequence(self, sequence):
    "Get the next value from a sequence."
    return sequence[(self.value - 1) % len(sequence)]

  def getroman(self):
    "Get the next value as a roman number."
    result = ''
    number = self.value
    for numeral, value in self.romannumerals:
      if number >= value:
        result += numeral * (number / value)
        number = number % value
    return result

  def getvalue(self):
    "Get the current value as configured in the current mode."
    if not self.mode or self.mode in ['text', '1']:
      return self.gettext()
    if self.mode == 'A':
      return self.getletter()
    if self.mode == 'a':
      return self.getletter().lower()
    if self.mode == 'I':
      return self.getroman()
    if self.mode == '*':
      return self.getsymbol()
    Trace.error('Unknown counter mode ' + self.mode)
    return self.gettext()

  def getnext(self):
    "Get the next value as configured: increase() and getvalue()."
    return self.increase().getvalue()

  def reset(self):
    "Reset the counter."
    self.value = 0

  def __unicode__(self):
    "Return a printable representation."
    result = 'Counter ' + self.name
    if self.mode:
      result += ' in mode ' + self.mode
    return result

class DependentCounter(NumberCounter):
  "A counter which depends on another one (the master)."

  def setmaster(self, master):
    "Set the master counter."
    self.master = master
    self.last = self.master.getvalue()
    return self

  def increase(self):
    "Increase or, if the master counter has changed, restart."
    if self.last != self.master.getvalue():
      self.reset()
    NumberCounter.increase(self)
    self.last = self.master.getvalue()
    return self

  def getvalue(self):
    "Get the value of the combined counter: master.dependent."
    return self.master.getvalue() + '.' + NumberCounter.getvalue(self)

class NumberGenerator(object):
  "A number generator for unique sequences and hierarchical structures. Used in:"
  "  * ordered part numbers: Chapter 3, Section 5.3."
  "  * unique part numbers: Footnote 15, Bibliography cite [15]."
  "  * chaptered part numbers: Figure 3.15, Equation (8.3)."
  "  * unique roman part numbers: Part I, Book IV."

  chaptered = None
  generator = None

  romanlayouts = [x.lower() for x in NumberingConfig.layouts['roman']]
  orderedlayouts = [x.lower() for x in NumberingConfig.layouts['ordered']]

  counters = dict()
  appendix = None

  def deasterisk(self, type):
    "Remove the possible asterisk in a layout type."
    return type.replace('*', '')

  def isunique(self, type):
    "Find out if the layout type corresponds to a unique part."
    return self.isroman(type)

  def isroman(self, type):
    "Find out if the layout type should have roman numeration."
    return self.deasterisk(type).lower() in self.romanlayouts

  def isinordered(self, type):
    "Find out if the layout type corresponds to an (un)ordered part."
    return self.deasterisk(type).lower() in self.orderedlayouts

  def isnumbered(self, type):
    "Find out if the type for a layout corresponds to a numbered layout."
    if '*' in type:
      return False
    if self.isroman(type):
      return True
    if not self.isinordered(type):
      return False
    if self.getlevel(type) > DocumentParameters.maxdepth:
      return False
    return True

  def isunordered(self, type):
    "Find out if the type contains an asterisk, basically."
    return '*' in type

  def getlevel(self, type):
    "Get the level that corresponds to a layout type."
    if self.isunique(type):
      return 0
    if not self.isinordered(type):
      Trace.error('Unknown layout type ' + type)
      return 0
    type = self.deasterisk(type).lower()
    level = self.orderedlayouts.index(type) + 1
    return level - DocumentParameters.startinglevel

  def getparttype(self, type):
    "Obtain the type for the part: without the asterisk, "
    "and switched to Appendix if necessary."
    if NumberGenerator.appendix and self.getlevel(type) == 1:
      return 'Appendix'
    return self.deasterisk(type)

  def generate(self, type):
    "Generate a number for a layout type."
    "Unique part types such as Part or Book generate roman numbers: Part I."
    "Ordered part types return dot-separated tuples: Chapter 5, Subsection 2.3.5."
    "Everything else generates unique numbers: Bibliography [1]."
    "Each invocation results in a new number."
    return self.getcounter(type).getnext()

  def getcounter(self, type):
    "Get the counter for the given type."
    type = type.lower()
    if not type in self.counters:
      self.counters[type] = self.create(type)
    return self.counters[type]

  def create(self, type):
    "Create a counter for the given type."
    if self.isnumbered(type) and self.getlevel(type) > 1:
      index = self.orderedlayouts.index(type)
      above = self.orderedlayouts[index - 1]
      master = self.getcounter(above)
      return self.createdependent(type, master)
    counter = NumberCounter(type)
    if self.isroman(type):
      counter.setmode('I')
    return counter

  def getdependentcounter(self, type, master):
    "Get (or create) a counter of the given type that depends on another."
    if not type in self.counters or not self.counters[type].master:
      self.counters[type] = self.createdependent(type, master)
    return self.counters[type]

  def createdependent(self, type, master):
    "Create a dependent counter given the master."
    return DependentCounter(type).setmaster(master)

  def startappendix(self):
    "Start appendices here."
    firsttype = self.orderedlayouts[DocumentParameters.startinglevel]
    counter = self.getcounter(firsttype)
    counter.setmode('A').reset()
    NumberGenerator.appendix = True

class ChapteredGenerator(NumberGenerator):
  "Generate chaptered numbers, as in Chapter.Number."
  "Used in equations, figures: Equation (5.3), figure 8.15."

  def generate(self, type):
    "Generate a number which goes with first-level numbers (chapters). "
    "For the article classes a unique number is generated."
    if DocumentParameters.startinglevel > 0:
      return NumberGenerator.generator.generate(type)
    chapter = self.getcounter('Chapter')
    return self.getdependentcounter(type, chapter).getnext()


NumberGenerator.chaptered = ChapteredGenerator()
NumberGenerator.generator = NumberGenerator()






class ContainerSize(object):
  "The size of a container."

  width = None
  height = None
  maxwidth = None
  maxheight = None
  scale = None

  def set(self, width = None, height = None):
    "Set the proper size with width and height."
    self.setvalue('width', width)
    self.setvalue('height', height)
    return self

  def setmax(self, maxwidth = None, maxheight = None):
    "Set max width and/or height."
    self.setvalue('maxwidth', maxwidth)
    self.setvalue('maxheight', maxheight)
    return self

  def readparameters(self, container):
    "Read some size parameters off a container."
    self.setparameter(container, 'width')
    self.setparameter(container, 'height')
    self.setparameter(container, 'scale')
    self.checkvalidheight(container)
    return self

  def setparameter(self, container, name):
    "Read a size parameter off a container, and set it if present."
    value = container.getparameter(name)
    self.setvalue(name, value)

  def setvalue(self, name, value):
    "Set the value of a parameter name, only if it's valid."
    value = self.processparameter(value)
    if value:
      setattr(self, name, value)

  def checkvalidheight(self, container):
    "Check if the height parameter is valid; otherwise erase it."
    heightspecial = container.getparameter('height_special')
    if self.height and self.extractnumber(self.height) == '1' and heightspecial == 'totalheight':
      self.height = None

  def processparameter(self, value):
    "Do the full processing on a parameter."
    if not value:
      return None
    if self.extractnumber(value) == '0':
      return None
    for ignored in StyleConfig.size['ignoredtexts']:
      if ignored in value:
        value = value.replace(ignored, '')
    return value

  def extractnumber(self, text):
    "Extract the first number in the given text."
    result = ''
    decimal = False
    for char in text:
      if char.isdigit():
        result += char
      elif char == '.' and not decimal:
        result += char
        decimal = True
      else:
        return result
    return result

  def checkimage(self, width, height):
    "Check image dimensions, set them if possible."
    if width:
      self.maxwidth = unicode(width) + 'px'
      if self.scale and not self.width:
        self.width = self.scalevalue(width)
    if height:
      self.maxheight = unicode(height) + 'px'
      if self.scale and not self.height:
        self.height = self.scalevalue(height)
    if self.width and not self.height:
      self.height = 'auto'
    if self.height and not self.width:
      self.width = 'auto'

  def scalevalue(self, value):
    "Scale the value according to the image scale and return it as unicode."
    scaled = value * int(self.scale) / 100
    return unicode(int(scaled)) + 'px'

  def removepercentwidth(self):
    "Remove percent width if present, to set it at the figure level."
    if not self.width:
      return None
    if not '%' in self.width:
      return None
    width = self.width
    self.width = None
    if self.height == 'auto':
      self.height = None
    return width

  def addstyle(self, container):
    "Add the proper style attribute to the output tag."
    if not isinstance(container.output, TaggedOutput):
      Trace.error('No tag to add style, in ' + unicode(container))
    if not self.width and not self.height and not self.maxwidth and not self.maxheight:
      # nothing to see here; move along
      return
    tag = ' style="'
    tag += self.styleparameter('width')
    tag += self.styleparameter('maxwidth')
    tag += self.styleparameter('height')
    tag += self.styleparameter('maxheight')
    if tag[-1] == ' ':
      tag = tag[:-1]
    tag += '"'
    container.output.tag += tag

  def styleparameter(self, name):
    "Get the style for a single parameter."
    value = getattr(self, name)
    if value:
      return name.replace('max', 'max-') + ': ' + value + '; '
    return ''



class QuoteContainer(Container):
  "A container for a pretty quote"

  def __init__(self):
    self.parser = BoundedParser()
    self.output = FixedOutput()

  def process(self):
    "Process contents"
    self.type = self.header[2]
    if not self.type in StyleConfig.quotes:
      Trace.error('Quote type ' + self.type + ' not found')
      self.html = ['"']
      return
    self.html = [StyleConfig.quotes[self.type]]

class LyXLine(Container):
  "A Lyx line"

  def __init__(self):
    self.parser = LoneCommand()
    self.output = FixedOutput()

  def process(self):
    self.html = ['<hr class="line" />']

class EmphaticText(TaggedText):
  "Text with emphatic mode"

  def process(self):
    self.output.tag = 'i'

class ShapedText(TaggedText):
  "Text shaped (italic, slanted)"

  def process(self):
    self.type = self.header[1]
    if not self.type in TagConfig.shaped:
      Trace.error('Unrecognized shape ' + self.header[1])
      self.output.tag = 'span'
      return
    self.output.tag = TagConfig.shaped[self.type]

class VersalitasText(TaggedText):
  "Text in versalitas"

  def process(self):
    self.output.tag = 'span class="versalitas"'

class ColorText(TaggedText):
  "Colored text"

  def process(self):
    self.color = self.header[1]
    self.output.tag = 'span class="' + self.color + '"'

class SizeText(TaggedText):
  "Sized text"

  def process(self):
    self.size = self.header[1]
    self.output.tag = 'span class="' + self.size + '"'

class BoldText(TaggedText):
  "Bold text"

  def process(self):
    self.output.tag = 'b'

class TextFamily(TaggedText):
  "A bit of text from a different family"

  def process(self):
    "Parse the type of family"
    self.type = self.header[1]
    if not self.type in TagConfig.family:
      Trace.error('Unrecognized family ' + type)
      self.output.tag = 'span'
      return
    self.output.tag = TagConfig.family[self.type]

class Hfill(TaggedText):
  "Horizontall fill"

  def process(self):
    self.output.tag = 'span class="hfill"'

class BarredText(TaggedText):
  "Text with a bar somewhere"

  def process(self):
    "Parse the type of bar"
    self.type = self.header[1]
    if not self.type in TagConfig.barred:
      Trace.error('Unknown bar type ' + self.type)
      self.output.tag = 'span'
      return
    self.output.tag = TagConfig.barred[self.type]

class LangLine(BlackBox):
  "A line with language information"

  def process(self):
    self.lang = self.header[1]

class InsetLength(BlackBox):
  "A length measure inside an inset."

  def process(self):
    self.length = self.header[1]

class Space(Container):
  "A space of several types"

  def __init__(self):
    self.parser = InsetParser()
    self.output = FixedOutput()
  
  def process(self):
    self.type = self.header[2]
    if self.type not in StyleConfig.hspaces:
      Trace.error('Unknown space type ' + self.type)
      self.html = [' ']
      return
    self.html = [StyleConfig.hspaces[self.type]]
    length = self.getlength()
    if not length:
      return
    self.output = TaggedOutput().settag('span class="hspace"', False)
    ContainerSize().set(length).addstyle(self)

  def getlength(self):
    "Get the space length from the contents or parameters."
    if len(self.contents) == 0 or not isinstance(self.contents[0], InsetLength):
      return None
    return self.contents[0].length

class VerticalSpace(Container):
  "An inset that contains a vertical space."

  def __init__(self):
    self.parser = InsetParser()
    self.output = FixedOutput()

  def process(self):
    "Set the correct tag"
    self.type = self.header[2]
    if self.type not in StyleConfig.vspaces:
      self.output = TaggedOutput().settag('div class="vspace" style="height: ' + self.type + ';"', True)
      return
    self.html = [StyleConfig.vspaces[self.type]]

class Align(Container):
  "Bit of aligned text"

  def __init__(self):
    self.parser = ExcludingParser()
    self.output = TaggedOutput().setbreaklines(True)

  def process(self):
    self.output.tag = 'div class="' + self.header[1] + '"'

class Newline(Container):
  "A newline"

  def __init__(self):
    self.parser = LoneCommand()
    self.output = FixedOutput()

  def process(self):
    "Process contents"
    self.html = ['<br/>\n']

class NewPage(Newline):
  "A new page"

  def process(self):
    "Process contents"
    self.html = ['<p><br/>\n</p>\n']

class Separator(Container):
  "A separator string which is not extracted by extracttext()."

  def __init__(self, constant):
    self.output = FixedOutput()
    self.contents = []
    self.html = [constant]

class StartAppendix(BlackBox):
  "Mark to start an appendix here."
  "From this point on, all chapters become appendices."

  def process(self):
    "Activate the special numbering scheme for appendices, using letters."
    NumberGenerator.generator.startappendix()

class ERT(Container):
  "Evil Red Text"

  def __init__(self):
    self.parser = InsetParser()
    self.output = EmptyOutput()






class Link(Container):
  "A link to another part of the document"

  anchor = None
  url = None
  type = None
  page = None
  target = None
  destination = None
  title = None

  def __init__(self):
    "Initialize the link, add target if configured."
    self.contents = []
    self.parser = InsetParser()
    self.output = LinkOutput()
    if Options.target:
      self.target = Options.target

  def complete(self, text, anchor = None, url = None, type = None, title = None):
    "Complete the link."
    self.contents = [Constant(text)]
    if anchor:
      self.anchor = anchor
    if url:
      self.url = url
    if type:
      self.type = type
    if title:
      self.title = title
    return self

  def computedestination(self):
    "Use the destination link to fill in the destination URL."
    if not self.destination:
      return
    self.url = ''
    if self.destination.anchor:
      self.url = '#' + self.destination.anchor
    if self.destination.page:
      self.url = self.destination.page + self.url

  def setmutualdestination(self, destination):
    "Set another link as destination, and set its destination to this one."
    self.destination = destination
    destination.destination = self

  def __unicode__(self):
    "Return a printable representation."
    result = 'Link'
    if self.anchor:
      result += ' #' + self.anchor
    if self.url:
      result += ' to ' + self.url
    return result

class URL(Link):
  "A clickable URL"

  def process(self):
    "Read URL from parameters"
    target = self.escape(self.getparameter('target'))
    self.url = target
    type = self.getparameter('type')
    if type:
      self.url = self.escape(type) + target
    name = self.getparameter('name')
    if not name:
      name = target
    self.contents = [Constant(name)]

class FlexURL(URL):
  "A flexible URL"

  def process(self):
    "Read URL from contents"
    self.url = self.extracttext()

class LinkOutput(ContainerOutput):
  "A link pointing to some destination"
  "Or an anchor (destination)"

  def gethtml(self, link):
    "Get the HTML code for the link"
    type = link.__class__.__name__
    if link.type:
      type = link.type
    tag = 'a class="' + type + '"'
    if link.anchor:
      tag += ' name="' + link.anchor + '"'
    if link.destination:
      link.computedestination()
    if link.url:
      tag += ' href="' + link.url + '"'
    if link.target:
      tag += ' target="' + link.target + '"'
    if link.title:
      tag += ' title="' + link.title + '"'
    return TaggedOutput().settag(tag).gethtml(link)





class Postprocessor(object):
  "Postprocess a container keeping some context"

  stages = []

  def __init__(self):
    self.stages = StageDict(Postprocessor.stages, self)
    self.current = None
    self.last = None

  def postprocess(self, next):
    "Postprocess a container and its contents."
    self.postrecursive(self.current)
    result = self.postcurrent(next)
    self.last = self.current
    self.current = next
    return result

  def postrecursive(self, container):
    "Postprocess the container contents recursively"
    if not hasattr(container, 'contents'):
      return
    if len(container.contents) == 0:
      return
    if hasattr(container, 'postprocess'):
      if not container.postprocess:
        return
    postprocessor = Postprocessor()
    contents = []
    for element in container.contents:
      post = postprocessor.postprocess(element)
      if post:
        contents.append(post)
    # two rounds to empty the pipeline
    for i in range(2):
      post = postprocessor.postprocess(None)
      if post:
        contents.append(post)
    container.contents = contents

  def postcurrent(self, next):
    "Postprocess the current element taking into account next and last."
    stage = self.stages.getstage(self.current)
    if not stage:
      return self.current
    return stage.postprocess(self.last, self.current, next)

class StageDict(object):
  "A dictionary of stages corresponding to classes"

  def __init__(self, classes, postprocessor):
    "Instantiate an element from each class and store as a dictionary"
    instances = self.instantiate(classes, postprocessor)
    self.stagedict = dict([(x.processedclass, x) for x in instances])

  def instantiate(self, classes, postprocessor):
    "Instantiate an element from each class"
    stages = [x.__new__(x) for x in classes]
    for element in stages:
      element.__init__()
      element.postprocessor = postprocessor
    return stages

  def getstage(self, element):
    "Get the stage for a given element, if the type is in the dict"
    if not element.__class__ in self.stagedict:
      return None
    return self.stagedict[element.__class__]



class Label(Link):
  "A label to be referenced"

  names = dict()
  lastlayout = None

  def __init__(self):
    Link.__init__(self)
    self.lastnumbered = None

  def process(self):
    "Process a label container."
    key = self.getparameter('name')
    self.create(' ', key)
    self.lastnumbered = Label.lastlayout

  def create(self, text, key, type = 'Label'):
    "Create the label for a given key."
    self.key = key
    self.complete(text, anchor = key, type = type)
    Label.names[key] = self
    if key in Reference.references:
      for reference in Reference.references[key]:
        reference.destination = self
    return self

  def labelnumber(self):
    "Get the number for the latest numbered container seen."
    numbered = self.numbered(self)
    if numbered and numbered.partkey and numbered.partkey.number:
      return numbered.partkey.number
    return ''

  def numbered(self, container):
    "Get the numbered container for the label."
    if container.partkey:
      return container
    if not container.parent:
      if self.lastnumbered:
        return self.lastnumbered
      return None
    return self.numbered(container.parent)

  def __unicode__(self):
    "Return a printable representation."
    if not hasattr(self, 'key'):
      return 'Unnamed label'
    return 'Label ' + self.key

class Reference(Link):
  "A reference to a label."

  references = dict()
  formats = {
      'ref':u'@↕', 'eqref':u'(@↕)', 'pageref':u'#↕',
      'vref':u'@on-page#↕'
      }
  key = 'none'

  def process(self):
    "Read the reference and set the arrow."
    self.key = self.getparameter('reference')
    if self.key in Label.names:
      self.direction = u'↑'
      label = Label.names[self.key]
    else:
      self.direction = u'↓'
      label = Label().complete(' ', self.key, 'preref')
    self.destination = label
    self.format()
    if not self.key in Reference.references:
      Reference.references[self.key] = []
    Reference.references[self.key].append(self)

  def format(self):
    "Format the reference contents."
    formatkey = self.getparameter('LatexCommand')
    if not formatkey:
      formatkey = 'ref'
    if not formatkey in self.formats:
      Trace.error('Unknown reference format ' + formatkey)
      formatstring = u'↕'
    else:
      formatstring = self.formats[formatkey]
    formatstring = formatstring.replace(u'↕', self.direction)
    formatstring = formatstring.replace('@', self.destination.labelnumber())
    formatstring = formatstring.replace('#', '1')
    formatstring = formatstring.replace('on-page', Translator.translate('on-page'))
    self.contents = [Constant(formatstring)]

  def __unicode__(self):
    "Return a printable representation."
    return 'Reference ' + self.key



class FormulaCommand(FormulaBit):
  "A LaTeX command inside a formula"

  types = []
  start = FormulaConfig.starts['command']

  def detect(self, pos):
    "Find the current command"
    return pos.checkfor(FormulaCommand.start)

  def parsebit(self, pos):
    "Parse the command"
    command = self.extractcommand(pos)
    for type in FormulaCommand.types:
      if command in type.commandmap:
        newbit = self.factory.create(type)
        newbit.setcommand(command)
        newbit.parsebit(pos)
        self.add(newbit)
        return newbit
    if not self.factory.defining:
      Trace.error('Unknown command ' + command)
    self.output = TaggedOutput().settag('span class="unknown"')
    self.add(FormulaConstant(command))
    return None

  def extractcommand(self, pos):
    "Extract the command from the current position"
    if not pos.checkskip(FormulaCommand.start):
      Trace.error('Missing command start ' + start)
      return
    if pos.current().isalpha():
      # alpha command
      command = FormulaCommand.start + pos.globalpha()
      # skip mark of short command
      pos.checkskip('*')
      return command
    # symbol command
    return FormulaCommand.start + pos.skipcurrent()

class CommandBit(FormulaCommand):
  "A formula bit that includes a command"

  def setcommand(self, command):
    "Set the command in the bit"
    self.command = command
    self.original += command
    self.translated = self.commandmap[self.command]
 
  def parseparameter(self, pos):
    "Parse a parameter at the current position"
    if not self.factory.detectany(pos):
      Trace.error('No parameter found at: ' + pos.identifier())
      return None
    parameter = self.factory.parseany(pos)
    self.add(parameter)
    return parameter

  def parsesquare(self, pos):
    "Parse a square bracket"
    if not self.factory.detecttype(SquareBracket, pos):
      return None
    bracket = self.factory.parsetype(SquareBracket, pos)
    self.add(bracket)
    return bracket

  def parseliteral(self, pos):
    "Parse a literal bracket."
    if not self.factory.detecttype(Bracket, pos):
      Trace.error('No literal parameter found at: ' + pos.identifier())
      return None
    bracket = Bracket().setfactory(self.factory)
    self.add(bracket.parseliteral(pos))
    return bracket.literal

  def parsesquareliteral(self, pos):
    "Parse a square bracket literally."
    if not self.factory.detecttype(SquareBracket, pos):
      return None
    bracket = SquareBracket().setfactory(self.factory)
    self.add(bracket.parseliteral(pos))
    return bracket.literal

class EmptyCommand(CommandBit):
  "An empty command (without parameters)"

  commandmap = FormulaConfig.commands

  def parsebit(self, pos):
    "Parse a command without parameters"
    self.contents = [FormulaConstant(self.translated)]

class AlphaCommand(EmptyCommand):
  "A command without paramters whose result is alphabetical"

  commandmap = FormulaConfig.alphacommands

  def parsebit(self, pos):
    "Parse the command and set type to alpha"
    EmptyCommand.parsebit(self, pos)
    self.type = 'alpha'

class OneParamFunction(CommandBit):
  "A function of one parameter"

  commandmap = FormulaConfig.onefunctions

  def parsebit(self, pos):
    "Parse a function with one parameter"
    self.output = TaggedOutput().settag(self.translated)
    self.parseparameter(pos)
    self.simplifyifpossible()

  def simplifyifpossible(self):
    "Try to simplify to a single character."
    if self.original in self.commandmap:
      self.output = FixedOutput()
      self.html = [self.commandmap[self.original]]

class SymbolFunction(CommandBit):
  "Find a function which is represented by a symbol (like _ or ^)"

  commandmap = FormulaConfig.symbolfunctions

  def detect(self, pos):
    "Find the symbol"
    return pos.current() in SymbolFunction.commandmap

  def parsebit(self, pos):
    "Parse the symbol"
    self.setcommand(pos.current())
    pos.skip(self.command)
    self.output = TaggedOutput().settag(self.translated)
    self.parseparameter(pos)

class TextFunction(CommandBit):
  "A function where parameters are read as text."

  commandmap = FormulaConfig.textfunctions

  def parsebit(self, pos):
    "Parse a text parameter"
    self.output = TaggedOutput().settag(self.translated)
    if not self.factory.detecttype(Bracket, pos):
      Trace.error('No parameter for ' + unicode(self))
    bracket = Bracket().setfactory(self.factory).parsetext(pos)
    self.add(bracket)

  def process(self):
    "Set the type to font"
    self.type = 'font'

class LabelFunction(CommandBit):
  "A function that acts as a label"

  commandmap = FormulaConfig.labelfunctions

  def parsebit(self, pos):
    "Parse a literal parameter"
    self.key = self.parseliteral(pos)

  def process(self):
    "Add an anchor with the label contents."
    self.type = 'font'
    self.label = Label().create(' ', self.key, type = 'eqnumber')
    self.contents = [self.label]
    # store as a Label so we know it's been seen
    Label.names[self.key] = self.label

class FontFunction(OneParamFunction):
  "A function of one parameter that changes the font"

  commandmap = FormulaConfig.fontfunctions

  def process(self):
    "Simplify if possible using a single character."
    self.type = 'font'
    self.simplifyifpossible()

class CombiningFunction(OneParamFunction):

  commandmap = FormulaConfig.combiningfunctions

  def parsebit(self, pos):
    "Parse a combining function."
    self.type = 'alpha'
    combining = self.translated
    parameter = self.parseparameter(pos)
    if len(parameter.extracttext()) != 1:
      Trace.error('Applying combining function to invalid string ' + parameter.extracttext())
    self.contents.append(Constant(combining))

class DecoratingFunction(OneParamFunction):
  "A function that decorates some bit of text"

  commandmap = FormulaConfig.decoratingfunctions

  def parsebit(self, pos):
    "Parse a decorating function"
    self.type = 'alpha'
    symbol = self.translated
    self.symbol = TaggedBit().constant(symbol, 'span class="symbolover"')
    self.parameter = self.parseparameter(pos)
    self.output = TaggedOutput().settag('span class="withsymbol"')
    self.contents.insert(0, self.symbol)
    self.parameter.output = TaggedOutput().settag('span class="undersymbol"')
    self.simplifyifpossible()

FormulaFactory.types += [FormulaCommand, SymbolFunction]
FormulaCommand.types = [
    EmptyCommand, AlphaCommand, OneParamFunction, DecoratingFunction,
    FontFunction, LabelFunction, TextFunction, CombiningFunction,
    ]






class ParameterDefinition(object):
  "The definition of a parameter in a hybrid function."
  "[] parameters are optional, {} parameters are mandatory."
  "Each parameter has a one-character name, like {$1} or {$p}."
  "A parameter that ends in ! like {$p!} is a literal."
  "Example: [$1]{$p!} reads an optional parameter $1 and a literal mandatory parameter p."

  parambrackets = [('[', ']'), ('{', '}')]

  def __init__(self):
    self.name = None
    self.literal = False
    self.optional = False
    self.value = None
    self.literalvalue = None

  def parse(self, pos):
    "Parse a parameter definition: [$0], {$x}, {$1!}..."
    for (opening, closing) in ParameterDefinition.parambrackets:
      if pos.checkskip(opening):
        if opening == '[':
          self.optional = True
        if not pos.checkskip('$'):
          Trace.error('Wrong parameter name ' + pos.current())
          return None
        self.name = pos.skipcurrent()
        if pos.checkskip('!'):
          self.literal = True
        if not pos.checkskip(closing):
          Trace.error('Wrong parameter closing ' + pos.skipcurrent())
          return None
        return self
    Trace.error('Wrong character in parameter template: ' + pos.skipcurrent())
    return None

  def read(self, pos, function):
    "Read the parameter itself using the definition."
    if self.literal:
      if self.optional:
        self.literalvalue = function.parsesquareliteral(pos)
      else:
        self.literalvalue = function.parseliteral(pos)
      if self.literalvalue:
        self.value = FormulaConstant(self.literalvalue)
    elif self.optional:
      self.value = function.parsesquare(pos)
    else:
      self.value = function.parseparameter(pos)

  def __unicode__(self):
    "Return a printable representation."
    result = 'param ' + self.name
    if self.value:
      result += ': ' + unicode(self.value)
    else:
      result += ' (empty)'
    return result

class ParameterFunction(CommandBit):
  "A function with a variable number of parameters defined in a template."
  "The parameters are defined as a parameter definition."

  def readparams(self, readtemplate, pos):
    "Read the params according to the template."
    self.params = dict()
    for paramdef in self.paramdefs(readtemplate):
      paramdef.read(pos, self)
      self.params['$' + paramdef.name] = paramdef

  def paramdefs(self, readtemplate):
    "Read each param definition in the template"
    pos = TextPosition(readtemplate)
    while not pos.finished():
      paramdef = ParameterDefinition().parse(pos)
      if paramdef:
        yield paramdef

  def getparam(self, name):
    "Get a parameter as parsed."
    if not name in self.params:
      return None
    return self.params[name]

  def getvalue(self, name):
    "Get the value of a parameter."
    return self.getparam(name).value

  def getliteralvalue(self, name):
    "Get the literal value of a parameter."
    param = self.getparam(name)
    if not param or not param.literalvalue:
      return None
    return param.literalvalue

  def getintvalue(self, name):
    "Get the value of a literal parameter as an int."
    value = self.getliteralvalue(name)
    if not value:
      return 0
    return int(value)

class HybridFunction(ParameterFunction):
  """
  A parameter function where the output is also defined using a template.
  The template can use a number of functions; each function has an associated tag.
  Example: [f0{$1},span class="fbox"] defines a function f0 which corresponds to
  a span of class fbox, yielding <span class="fbox">$1</span>.
  Literal parameters can be used in tags definitions: [f0{$1},span style="color: $p;"]
  yields <span style="color: $p;">$1</span>, where $p is a literal parameter.
  """

  commandmap = FormulaConfig.hybridfunctions

  def parsebit(self, pos):
    "Parse a function with [] and {} parameters"
    readtemplate = self.translated[0]
    writetemplate = self.translated[1]
    self.readparams(readtemplate, pos)
    self.contents = self.writeparams(writetemplate)

  def writeparams(self, writetemplate):
    "Write all params according to the template"
    return self.writepos(TextPosition(writetemplate))

  def writepos(self, pos):
    "Write all params as read in the parse position."
    result = []
    while not pos.finished():
      if pos.checkskip('$'):
        param = self.writeparam(pos)
        if param:
          result.append(param)
      elif pos.checkskip('f'):
        function = self.writefunction(pos)
        if function:
          result.append(function)
      else:
        result.append(FormulaConstant(pos.skipcurrent()))
    return result

  def writeparam(self, pos):
    "Write a single param of the form $0, $x..."
    name = '$' + pos.skipcurrent()
    if not name in self.params:
      Trace.error('Unknown parameter ' + name)
      return None
    if not self.params[name]:
      return None
    if pos.checkskip('.'):
      self.params[name].value.type = pos.globalpha()
    return self.params[name].value

  def writefunction(self, pos):
    "Write a single function f0,...,fn."
    tag = self.readtag(pos)
    if not tag:
      return None
    if not pos.checkskip('{'):
      Trace.error('Function should be defined in {}')
      return None
    pos.pushending('}')
    contents = self.writepos(pos)
    pos.popending()
    if len(contents) == 0:
      return None
    function = TaggedBit().complete(contents, tag)
    function.type = None
    return function

  def readtag(self, pos):
    "Get the tag corresponding to the given index. Does parameter substitution."
    if not pos.current().isdigit():
      Trace.error('Function should be f0,...,f9: f' + pos.current())
      return None
    index = int(pos.skipcurrent())
    if 2 + index > len(self.translated):
      Trace.error('Function f' + unicode(index) + ' is not defined')
      return None
    tag = self.translated[2 + index]
    if not '$' in tag:
      return tag
    for variable in self.params:
      if variable in tag:
        param = self.params[variable]
        if not param.literal:
          Trace.error('Parameters in tag ' + tag + ' should be literal: {' + variable + '!}')
          continue
        if param.literalvalue:
          value = param.literalvalue
        else:
          value = ''
        tag = tag.replace(variable, value)
    return tag

FormulaCommand.types += [HybridFunction]






class FormulaEquation(CommandBit):
  "A simple numbered equation."

  piece = 'equation'

  def parsebit(self, pos):
    "Parse the array"
    self.output = ContentsOutput()
    self.add(self.factory.parsetype(WholeFormula, pos))

class FormulaCell(FormulaCommand):
  "An array cell inside a row"

  def setalignment(self, alignment):
    self.alignment = alignment
    self.output = TaggedOutput().settag('td class="formula-' + alignment +'"', True)
    return self

  def parsebit(self, pos):
    self.factory.clearignored(pos)
    if pos.finished():
      return
    if not self.factory.detecttype(WholeFormula, pos):
      Trace.error('Unexpected end of array cell at ' + pos.identifier())
      pos.skip(pos.current())
      return
    self.add(self.factory.parsetype(WholeFormula, pos))

class FormulaRow(FormulaCommand):
  "An array row inside an array"

  cellseparator = FormulaConfig.array['cellseparator']

  def setalignments(self, alignments):
    self.alignments = alignments
    self.output = TaggedOutput().settag('tr', True)
    return self

  def parsebit(self, pos):
    "Parse a whole row"
    index = 0
    pos.pushending(self.cellseparator, optional=True)
    while not pos.finished():
      alignment = self.alignments[index % len(self.alignments)]
      cell = self.factory.create(FormulaCell).setalignment(alignment)
      cell.parsebit(pos)
      self.add(cell)
      index += 1
      pos.checkskip(self.cellseparator)
    if len(self.contents) == 0:
      self.output = EmptyOutput()

class MultiRowFormula(CommandBit):
  "A formula with multiple rows."

  def parserows(self, pos):
    "Parse all rows, finish when no more row ends"
    for row in self.iteraterows(pos):
      row.parsebit(pos)
      self.add(row)

  def iteraterows(self, pos):
    "Iterate over all rows, end when no more row ends"
    rowseparator = FormulaConfig.array['rowseparator']
    while True:
      pos.pushending(rowseparator, True)
      row = self.factory.create(FormulaRow)
      yield row.setalignments(self.alignments)
      if pos.checkfor(rowseparator):
        self.original += pos.popending(rowseparator)
      else:
        return

class FormulaArray(MultiRowFormula):
  "An array within a formula"

  piece = 'array'

  def parsebit(self, pos):
    "Parse the array"
    self.output = TaggedOutput().settag('table class="formula"', True)
    self.parsealignments(pos)
    self.parserows(pos)

  def parsealignments(self, pos):
    "Parse the different alignments"
    # vertical
    self.valign = 'c'
    literal = self.parsesquareliteral(pos)
    if literal:
      self.valign = literal
    # horizontal
    literal = self.parseliteral(pos)
    self.alignments = []
    for l in literal:
      self.alignments.append(l)

class FormulaCases(MultiRowFormula):
  "A cases statement"

  piece = 'cases'

  def parsebit(self, pos):
    "Parse the cases"
    self.output = TaggedOutput().settag('table class="cases"', True)
    self.alignments = ['l', 'l']
    self.parserows(pos)

class EquationEnvironment(MultiRowFormula):
  "A \\begin{}...\\end equation environment with rows and cells."

  def parsebit(self, pos):
    "Parse the whole environment."
    self.output = TaggedOutput().settag('table class="environment"', True)
    environment = self.piece.replace('*', '')
    if environment in FormulaConfig.environments:
      self.alignments = FormulaConfig.environments[environment]
    else:
      Trace.error('Unknown equation environment ' + self.piece)
      self.alignments = ['l']
    self.parserows(pos)

class BeginCommand(CommandBit):
  "A \\begin{}...\end command and what it entails (array, cases, aligned)"

  commandmap = {FormulaConfig.array['begin']:''}

  types = [FormulaEquation, FormulaArray, FormulaCases]

  def parsebit(self, pos):
    "Parse the begin command"
    command = self.parseliteral(pos)
    bit = self.findbit(command)
    ending = FormulaConfig.array['end'] + '{' + command + '}'
    pos.pushending(ending)
    bit.parsebit(pos)
    self.add(bit)
    self.original += pos.popending(ending)

  def findbit(self, piece):
    "Find the command bit corresponding to the \\begin{piece}"
    for type in BeginCommand.types:
      if type.piece == piece:
        return self.factory.create(type)
    bit = self.factory.create(EquationEnvironment)
    bit.piece = piece
    return bit

FormulaCommand.types += [BeginCommand]









class HeaderParser(Parser):
  "Parses the LyX header"

  def parse(self, reader):
    "Parse header parameters into a dictionary, return the preamble."
    contents = []
    self.parseending(reader, lambda: self.parseline(reader, contents))
    # skip last line
    reader.nextline()
    return contents

  def parseline(self, reader, contents):
    "Parse a single line as a parameter or as a start"
    line = reader.currentline()
    if line.startswith(HeaderConfig.parameters['branch']):
      self.parsebranch(reader)
      return
    elif line.startswith(HeaderConfig.parameters['lstset']):
      LstParser().parselstset(reader)
      return
    elif line.startswith(HeaderConfig.parameters['beginpreamble']):
      contents.append(self.factory.createcontainer(reader))
      return
    # no match
    self.parseparameter(reader)

  def parsebranch(self, reader):
    "Parse all branch definitions."
    branch = reader.currentline().split()[1]
    reader.nextline()
    subparser = HeaderParser().complete(HeaderConfig.parameters['endbranch'])
    subparser.parse(reader)
    options = BranchOptions(branch)
    for key in subparser.parameters:
      options.set(key, subparser.parameters[key])
    Options.branches[branch] = options

  def complete(self, ending):
    "Complete the parser with the given ending."
    self.ending = ending
    return self

class PreambleParser(Parser):
  "A parser for the LyX preamble."

  preamble = []

  def parse(self, reader):
    "Parse the full preamble with all statements."
    self.ending = HeaderConfig.parameters['endpreamble']
    self.parseending(reader, lambda: self.parsepreambleline(reader))
    return []

  def parsepreambleline(self, reader):
    "Parse a single preamble line."
    PreambleParser.preamble.append(reader.currentline())
    reader.nextline()

class LstParser(object):
  "Parse global and local lstparams."

  globalparams = dict()

  def parselstset(self, reader):
    "Parse a declaration of lstparams in lstset."
    paramtext = self.extractlstset(reader)
    if not '{' in paramtext:
      Trace.error('Missing opening bracket in lstset: ' + paramtext)
      return
    lefttext = paramtext.split('{')[1]
    croppedtext = lefttext[:-1]
    LstParser.globalparams = self.parselstparams(croppedtext)

  def extractlstset(self, reader):
    "Extract the global lstset parameters."
    paramtext = ''
    while not reader.finished():
      paramtext += reader.currentline()
      reader.nextline()
      if paramtext.endswith('}'):
        return paramtext
    Trace.error('Could not find end of \\lstset settings; aborting')

  def parsecontainer(self, container):
    "Parse some lstparams from a container."
    container.lstparams = LstParser.globalparams.copy()
    paramlist = container.getparameterlist('lstparams')
    container.lstparams.update(self.parselstparams(paramlist))

  def parselstparams(self, paramlist):
    "Process a number of lstparams from a list."
    paramdict = dict()
    for param in paramlist:
      if not '=' in param:
        if len(param.strip()) > 0:
          Trace.error('Invalid listing parameter ' + param)
      else:
        key, value = param.split('=', 1)
        paramdict[key] = value
    return paramdict




class MathMacro(object):
  "A math macro: command, parameters, default values, definition."

  macros = dict()

  def __init__(self):
    self.newcommand = None
    self.parameternumber = 0
    self.defaults = []
    self.definition = None

  def instantiate(self):
    "Return an instance of the macro."
    return self.definition.clone()

class MacroParameter(FormulaBit):
  "A parameter from a macro."

  def detect(self, pos):
    "Find a macro parameter: #n."
    return pos.checkfor('#')

  def parsebit(self, pos):
    "Parse the parameter: #n."
    if not pos.checkskip('#'):
      Trace.error('Missing parameter start #.')
      return
    self.number = int(pos.skipcurrent())
    self.original = '#' + unicode(self.number)
    self.contents = [TaggedBit().constant('#' + unicode(self.number), 'span class="unknown"')]

class DefiningFunction(ParameterFunction):
  "Read a function that defines a new command (a macro)."

  commandmap = FormulaConfig.definingfunctions

  def parsebit(self, pos):
    "Parse a function with [] and {} parameters."
    if self.factory.detecttype(Bracket, pos):
      newcommand = self.parseliteral(pos)
    elif self.factory.detecttype(FormulaCommand, pos):
      newcommand = self.factory.create(FormulaCommand).extractcommand(pos)
    else:
      Trace.error('Unknown formula bit in defining function at ' + pos.identifier())
      return
    Trace.debug('New command: ' + newcommand)
    template = self.translated
    self.factory.defining = True
    self.readparams(template, pos)
    self.factory.defining = False
    self.contents = []
    macro = MathMacro()
    macro.newcommand = newcommand
    macro.parameternumber = self.getintvalue('$n')
    macro.definition = self.getvalue('$d')
    self.extractdefaults(macro)
    MathMacro.macros[newcommand] = macro

  def extractdefaults(self, macro):
    "Extract the default values for existing parameters."
    for index in range(9):
      value = self.extractdefault(index + 1)
      if value:
        macro.defaults.append(value)
      else:
        return

  def extractdefault(self, index):
    "Extract the default value for parameter index."
    value = self.getvalue('$' + unicode(index))
    if not value:
      return None
    if len(value.contents) == 0:
      return FormulaConstant('')
    return value.contents[0]

class MacroFunction(CommandBit):
  "A function that was defined using a macro."

  commandmap = MathMacro.macros

  def parsebit(self, pos):
    "Parse a number of input parameters."
    self.values = []
    macro = self.translated
    while self.factory.detecttype(Bracket, pos):
      self.values.append(self.parseparameter(pos))
    defaults = list(macro.defaults)
    remaining = macro.parameternumber - len(self.values) - len(defaults)
    if remaining > 0:
      self.parsenumbers(remaining, pos)
    while len(self.values) < macro.parameternumber and len(defaults) > 0:
      self.values.insert(0, defaults.pop())
    if len(self.values) < macro.parameternumber:
      Trace.error('Missing parameters in macro ' + unicode(self))
    self.completemacro(macro)

  def parsenumbers(self, remaining, pos):
    "Parse the remaining parameters as a running number."
    "For example, 12 would be {1}{2}."
    if pos.finished():
      return
    if not self.factory.detecttype(FormulaNumber, pos):
      return
    number = self.factory.parsetype(FormulaNumber, pos)
    if not len(number.original) == remaining:
      self.values.append(number)
      return
    for digit in number.original:
      value = self.factory.create(FormulaNumber)
      value.add(FormulaConstant(digit))
      value.type = number
      self.values.append(value)

  def completemacro(self, macro):
    "Complete the macro with the parameters read."
    self.contents = [macro.instantiate()]
    for parameter in self.searchall(MacroParameter):
      index = parameter.number - 1
      if index >= len(self.values):
        return
      parameter.contents = [self.values[index].clone()]

class FormulaMacro(Formula):
  "A math macro defined in an inset."

  def __init__(self):
    self.parser = MacroParser()
    self.output = EmptyOutput()

  def __unicode__(self):
    "Return a printable representation."
    return 'Math macro'

FormulaFactory.types += [ MacroParameter ]

FormulaCommand.types += [
    DefiningFunction, MacroFunction,
    ]



def math2html(formula):
  "Convert some TeX math to HTML."
  factory = FormulaFactory()
  whole = factory.parseformula(formula)
  FormulaProcessor().process(whole)
  whole.process()
  return ''.join(whole.gethtml())

def main():
  "Main function, called if invoked from the command line"
  if len(sys.argv) <= 1:
    Trace.error('Usage: math2html.py escaped_string')
    exit()
  result = math2html(sys.argv[1])
  Trace.message(result)

if __name__ == '__main__':
  main()

