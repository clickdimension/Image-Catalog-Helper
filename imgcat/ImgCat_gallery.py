#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  sdcat00001.py
#  
#  Copyright 2017  <oly_sop@oly_SOP-HP>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

import re
import os, sys, time, shutil, string
from PIL import Image, ExifTags
import Tkinter, tkFileDialog, tkMessageBox
import subprocess
#import codecs

import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

do_beep = 1


"""
sorry requires:
beep - for beep at dialog for new directory - tune /etc/modprobe.d/blacklist.conf:pcspkr - modprobe pcspkr
exiftool - for lensinfo of DSLR o ILC cameras (other info simply from PIL)


-- history:

15/12/2018:
html:
agregado fecha de primer foto en menu de directorios
index_th.js generado con comentario condicional si ya detecta placetags.js
img_thumb: mostrar solamente nombre de archivo en vez de ruta (nueva) completa
bug#: some backslash issues fixed when generating index.html, which prevented javascript loading


26/09/2018:
index.html/css, js.swapdetails: separacion visual de salto de mes en lista de miniaturas de imagenes
js:copy2box: al click sobre la imagen se copian datos - para copiar y crear lista de fotos "destacados"
js: "boton" nuevo para copiar y guardar placetags.js y filelist.txt  // pending: avoid duplicate !
js: placetags crean separación visual con titulo
img_getexit: rstrip("\0") to strip off invalid characters, appeared randomly in some img_getexif(thisimage, 'Model') info of old images of cell phones, utf8 maybe not neccessary


18/04/2018:
agregado opcion de S - dirsync, copy/update files into target tree


24/02/2018:
agregado os.beep antes de directorio nuevo - si el sistema lo soporta
bugfix - programa se cuelga cuando hay imagenes SIN exif !
call exiftool for lensinfo, no lo pude hacer con PIL, relevante hasta ahora solo para cameras DSLR o ILC (Nikon, Panasonic, etc + CanonPowerShotA540)


10/02/2018:
exif data in additional js columns:
ver info:
exiftool -T -r -filename -ExifVersion -make -model -LensID -FocalLength -FocalLengthIn35mmFormat -ExposureProgram -ExposureCompensation -ISO -fnumber -exposuretime ./
exiftool -s imagen.jpg

-model -LensID -FocalLength
-ISO -fnumber -exposuretime

29/10/2017:
bugfix in index.html/swapdetails: mostrar siempre subcat_name actual en titulo


10/08/2017:
index.js (master) + list.js por cada subdirectorio (antes: solo 1 subdirectorio), todos guardados en directorio inicial


03/08/2017: remaster de my_imgkat0904.py
increase thumb size from 200px to 400px


Resize an Image with PIL and Keep Aspect Ratio (Python)
This script will resize an image using PIL (Python Imaging Library) to a width of 200 pixels and a height proportional to the new width. It does this by determining what percentage 300 pixels is of the original width (img.size[0]) and then multiplying the original height (img.size[1]) by that percentage. Change "300" to any other number to change the default width of your images.


26/09/2017:
visually choose source + target dir (tkinter + Py2.x)
infos de imagen en lista: fecha, dimensiones...
segundo listado en index - archivos adicionales en carpetas ! (mov, txt, .nfo)
run option adicional: list only, clone dirtree, COPIAR archivos especiales desde carpeta original (txt, .nfo)
generate index.html if not exists, atencion: ya no hay link en imagenes apuntando al original
mostrar infos adicionales en thumbnail: fecha/dimensiones
end of program: info que directorio destino se utilizó, estadisticas ?


02/10/2017:
auto titulo por mes insertado entre las foto
run option adicional: select dir - scale all images
sudirectorio aunque quizas no haga falta


-- ideas:

use sox instead of beep:
https://stackoverflow.com/questions/16573051/sound-alarm-when-code-finishes
duration = 1  # second
freq = 440  # Hz
os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq))



extract images from file:

ffmpeg -i P1150329.MP4 -r 1  -ss 00:00:07 -t 00:00:11 -s 400x200 -f image2 image%03d.png

mp4 infos:
exiftool P1150329.MP4


 see https://github.com/chuckleplant/blog/blob/master/scripts/location-geotag.py -- use piexif
 https://github.com/hMatoba/Piexif
 https://www.blog.pythonlibrary.org/2010/03/28/getting-photo-metadata-exif-using-python/
 https://motherboard.vice.com/en_us/article/aekn58/hack-this-extra-image-metadata-using-python - with pillow/python3
 
 https://github.com/ianare/exif-py (exifread) ok, pero no incluye Panasonic tags :(
 
Warning: Invalid EXIF text encoding for UserComment 


    check py3.x compatible ?
    obviar tools externos: beep, exiftool ?
     
    run option adicional: list only + copy info files into cloned dir
    run option adicional: dirscan: create md5 list ?
     run option: clone dirtree - tambien desde directorio origen que no es formato DCIM original (clonar directorios de backup en blanco)
     run option: clone dirtree - opcion solamente clonar directorios base o hasta nivel xx
     run option: aceptar todos las siguientes preguntas yY 8seguir siguientes subdirectorios sin mas preguntas
    run option: check index.html need update ? (version indicator or checksum?)
    run option: no actualizar sub.js si contenido (nuevo) es identico
    
     end of program: estadisticas: si se scanea desde sd card - mostrar disk usage/free
     log messages: new month, files/bytes in last month

     exif: ExposureProgram, Flash, hdr/panorama/stacked
     mov-exif: show video thumbnail @10sec, movie data:resolution/Hz, total time, date time (start/save)

     image_thumb: .. alerta al eliminar imagen grande ? (cuidado - no eliminar originales !!)
     image_thumb: try create cuando archivo es corrupto o incorrecto ?
     image_thumb: rotar si necesario ?

    html: show statistics ? #/MB jpg, #/MB raw, #/MB MOV, #/MB thumbs
     html/js: mejorar auto-grupo de acuerdo a tag (ubicacion ?)
     js: eliminar cadena NULL (existe en nombre de camara/celular)
     html: de alguna forma mostrar imagenes con star o tag
     html: alinear a la derecha thumb grande que se muestran en el borde derecho
     
     
structure:

origen:
sd:/DCIM/123_PAN1
        /124_PAN2
        /124_PAN2/sub1
        /125_OTRO


creacion de thumbs en:
catalog:/destino/123_PAN1_th
        /124_PAN2_th
        /124_PAN2_th/sub1
        /125_OTRO_th

además archivos index:
catalog:/destino/index.html
        /index_th.js
        /123_PAN1_th.js
        /124_PAN2_th.js
        /125_OTRO_th.js

"""


def img_getexif00(imgin, exif_detail = 'size_str'):
    return_exif = ''

    if os.path.exists(imgin):
        img = Image.open(imgin)
        if exif_detail == 'size_str':
            return_exif = str(img.size[0]) + 'x' + str(img.size[1])
        else:
            for k, v in img._getexif().iteritems():
                if ExifTags.TAGS.get(k) == exif_detail:
                    return_exif = str(v)
    
    return return_exif


def img_getexif(imgin, exif_detail = 'size_str'):
    """
    requiere:
    exiftool (solo para funcion 'LensSpecification')
    """
    return_exif = ''

    #if os.path.exists(imgin):
    #    img = PIL.Image.open(imgin)
    #    print exif_detail
        
    if exif_detail == 'size_str':
        return_exif = str(imgin.size[0]) + 'x' + str(imgin.size[1])
    elif exif_detail == 'LensSpecification':
        # atencion argumento debe ser string, nombre de archivo nomas, no logre hacerlo con PIL solo
        #print subprocess.check_output(['exiftool', '-T', '-LensID', 'P1130720.JPG'])
        return_exif = subprocess.check_output(['exiftool', '-T', '-LensID', imgin]).strip()
    else:
        try:
            for k, v in imgin._getexif().iteritems():
                if ExifTags.TAGS.get(k) == exif_detail:
                    return_exif = str(v)
                    if type(v).__name__ in ('list', 'tuple'):
                        if len(v) == 2:
                            return_exif = '0'
                            if v[1] > 0:
                                return_exif = '{0:g}'.format(float(v[0])/v[1])
                            #if v[1] != 10 and v[0]>v[1]:
                            if v[1] > v[0]:
                                return_exif = '1/' + str('{0:g}'.format(float(v[1])/v[0]))
                        elif len(v) == 4:
                            #print return_exif
                            if type(v[0]).__name__ in ('list', 'tuple') and type(v[1]).__name__ in ('list', 'tuple'):
                                return_exif = str('{0:g}'.format(float(v[0][0])/v[0][1])) + '-' + str('{0:g}'.format(float(v[1][0])/v[1][1]))
                            if type(v[2]).__name__ in ('list', 'tuple') and type(v[3]).__name__ in ('list', 'tuple'):
                                if v[2] == v[3]:
                                    return_exif = return_exif + ' ' + str('{0:g}'.format(float(v[2][0])/v[2][1])) 
                                else:
                                    return_exif = return_exif + ' ' + str('{0:g}'.format(float(v[2][0])/v[2][1])) + '-' + str('{0:g}'.format(float(v[3][0])/v[3][1]))
                            else:
                                return_exif = return_exif + ' ++'

                        else:
                            print "convertir otro"
        except:
            return_exif = '-'
                       
    #return str(''.join(return_exif.split()))       # quitar los whitespace desde adentro
    return unicode(str(return_exif).rstrip("\0") , "utf-8")  #str(return_exif)        text.encode('utf-8') .strip('^@')


def img_size(imgin):
    """
    objetivo: mostrar info de imagen - dimensiones
    """
    dimension = ''

    if os.path.exists(imgin):
        img = Image.open(imgin)
        dimension = str(img.size[0]) + 'x' + str(img.size[1])
        
    return unicode(str(dimension), "utf-8")


def samefiles(file1, file2, ignore_date = True):
    
    if os.path.getsize(file1) != os.path.getsize(file2):
        print file1 + ' not same size'
        return False
        
    if not ignore_date and os.path.getmtime(file1) != os.path.getmtime(file2):
        print file1 + ' not same date'
        return False
        
    return True
        

def mk_dir(target_dir):
    """
    objetivo: crear directorio indicado, incluyendo todos los directorios "superiores" si faltan
    """

    #target_dir = os.path.split(imgout)[0]
    while not os.path.exists(target_dir):
        dirinferior=target_dir
        while not os.path.exists(os.path.split(dirinferior)[0]):
            dirinferior=os.path.split(dirinferior)[0]
        if dirinferior == target_dir:
            print "intento crear: " , target_dir
        os.mkdir(dirinferior)

    return 0
    

def img_thumb(imgin, imgout, newwidth = 200):
    """
    objetivo: crear thumbnail de archivos JPG
    """
    # check imgin
    # check imgout - eventualmente create dir, 
    # check imgout ya existe ? si incorrecto eliminar, si existe en subdir - mover, o crear
    # atencion panoramicos ...
    #print ".",
    target_dir = os.path.split(imgout)[0]
    # el siguiente while ya es obsoleto por la funcion mk_dir que se llama antes
    while not os.path.exists(target_dir):
        dirinferior=target_dir
        while not os.path.exists(os.path.split(dirinferior)[0]):
            dirinferior=os.path.split(dirinferior)[0]
        if dirinferior == target_dir:
            print "intento crear: " , target_dir
        os.mkdir(dirinferior)
        
    if os.path.exists(os.path.join(os.path.split(target_dir)[0], os.path.split(imgout)[1])):
        # TRY mover miniatura a directorio actual, overwrite if exists
        shutil.move(os.path.join(os.path.split(target_dir)[0], os.path.split(imgout)[1]), imgout)
        print ("//move: %s" % (os.path.join(os.path.split(target_dir)[1], os.path.split(imgout)[1])))
        # the only reason for shutil until now !!

    if os.path.exists(imgout):
        # verify size, eventualmente eliminar
        img = Image.open(imgout)
        if img.size[0] > newwidth or img.size[1] > newwidth:
            os.remove(imgout)
            print ("found too big: " + os.path.split(imgout)[1])
            
    if not os.path.exists(imgout):
        #print( imgout)
        print (os.path.split(imgout)[1])
        img = Image.open(imgin)
        #if not exif['Orientation']:
        #    img=img.rotate(90, expand=True)
        #img.thumbnail((1000,1000), Image.ANTIALIAS)
        if img.size[0] > newwidth and img.size[0] > img.size[1]:
            xpix = newwidth
            wpercent = (newwidth/float(img.size[0]))
            ypix = int((float(img.size[1])*float(wpercent)))
            try:
                img = img.resize((xpix,ypix), Image.ANTIALIAS)
            except:
                print "problema resize"
        elif img.size[1] > newwidth:
            # case image is portrait, may be square too
            ypix = newwidth
            wpercent = (newwidth/float(img.size[1]))
            xpix = int((float(img.size[0])*float(wpercent)))
            try:
                img = img.resize((xpix,ypix), Image.ANTIALIAS)
            except:
                print "problema resize"
        else:
            print ("copiando imagen chico: %d w x %d h" % (img.size[0], img.size[1]))
            # solamente copiar
            shutil.copy2(imgin, imgout)       # copiar sin preguntar
        print ("."), #"nuevo thumb"
        img.save(imgout) 
    
    return 0


def create_index(indexfile):
    htmlcontent = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

<head>
	<title>Lista de imagenes</title>
	<meta http-equiv="content-type" content="text/html;charset=utf-8" />
	<meta name="generator" content="Geany 1.27" />
<STYLE type="text/css">
<!--
html, body {
margin:0 25px 0 10px;
padding:0;
height:100%;
border:none;
font-family: verdana,sans;
}
A {TEXT-DECORATION: none;}

ul{padding: 0 5px 5px 5px; list-style-type: none;}
ul, li{margin: 0; border: 0;}
li A {TEXT-DECORATION: none; font-size: 11px;display: block;}

A:visited {TEXT-DECORATION: none}
A:active {TEXT-DECORATION: none}
A:hover {background-color: #DDEEFF; TEXT-DECORATION: underline}
a img{border: none;}
#contenttitle2{margin-bottom: 15px;}

#menucategory ul li{float: left;position: relative;padding: 5px;}
#menucategory ul ul{float: none;position:absolute;display: none;background:#CCCCCC;z-index: 200;}
#menucategory ul ul li{float: none;}
#menucategory ul li:hover ul{display: block;}

/*
#detalles {margin: 10px;}
*/
#detalles ul li {float: left;position: relative;padding: 5px;}
#detalles ul ul {position: absolute;z-index: 200;top: 30px;left: 20px;}
#detalles ul ul li {margin: 5px;background:#CCCCCC;}
#detalles ul ul {display: none;}
#detalles ul li:hover ul, #detalles ul ul li:hover {display: block;}

.monthbreak {clear: both; display: block; background:#D2E1EF;}
.tagbreak {clear: both; display: block; background:#F7E4B4;}

/*
#taglistdiv, #copylistdiv {position: absolute; left: -9999px;}
*/

-->
</STYLE>
<script type="text/javascript"  src="index_th.js"></script>
<script language="JavaScript">
<!--
thumb_js_skip = 0;		// thumb_js_skip usar para ocultar una parte inicial del menu de navegacion de subdirectorios

thumb_root = '';		// this index.html file is in the thumb_root directory, overwrite value of external javascript
// --- orig_root = orig_absroot;		// comentar esta linea, si los originales están en directorio "al lado"
orig_root = '../fotos/originales/copete/';
//orig_root = 'file:///' + orig_absroot;		// descomentar en caso windows, atender letra de unidad externa
// necesario adaptar thumb_root y orig_root, caso index.html fuera de la base de las imagenes en miniatura

//listfile = listfile_master[0]   //"imglist.js";
copyitems = 0;


function listas2menu(lista){

	content = ' ';
    if (lista[0].length > 0){
        content = content + '<ul>'
        for (var isub = 0; isub < lista[0].length; isub++ ) {
            //content = content + '<b>' + orig_root[lista[0][isub]] + ' &gt;&gt;</b> <ul><li><i>' + generated[lista[0][isub]] + '</i></li>';
            if (imagelist[lista[0][isub]].length > 0){
                content = content + '<li><b>' + lista[0][isub] + ' &gt;&gt;</b> <ul><li>desde: ' + imagelist[lista[0][isub]][0][1]+ '<hr><i>(generado: ' + generated[lista[0][isub]] + ')</i></li>';
            } else {
                content = content + '<li><b>' + lista[0][isub] + ' &gt;&gt;</b> <ul><li><i>' + generated[lista[0][isub]] + '</i></li>';
            }
            for ( var i = 0; i < dirlist[lista[0][isub]].length; i++) {
                //console.log(dirlist[lista[0][isub]][i] );
                content = content + '<li><a href="#" onclick="swapdetails('+ isub + ", " + i + ", 'contenttitle2', 'detalles');" +'">/' + dirlist[lista[0][isub]][i] + '</a></li>';
                //content = content + '<li><a href="#" onclick="swapdetails('+i+", dirlist, imagelist, 'contenttitle2', 'detalles');" + '">&nbsp;/' + lista[isub][i][0].substr(thumb_js_skip) + '</a></li>';
            } 
            content = content + '</ul></li>'
        }
        content = content + '</ul>'
    }
	document.getElementById('menucategory').innerHTML = content;
    if (placetags.length < 1) {
        document.getElementById('copyicons').innerHTML = '';        // no hay datos de comentarios de imagenes
    }
	return content;
}


function swapdetails(subcat, subdir, divtitulo, divdetail){
    subcat_name = dirlist[0][subcat];
	divcontent = '</b>' + subcat_name + ':</b> ';

	if (subdir > 0){
		divcontent = divcontent + '<a href="#" onclick="swapdetails(' + subcat + ", " + (subdir -1 ) + ", 'contenttitle2', 'detalles');" + '">&nbsp;/' + dirlist[subcat_name][subdir -1] + '</a> &lt; ';
	}
	divcontent = divcontent + '<b>/' + dirlist[subcat_name][subdir] + '</b> <i>(' + (subdir + 1) + '/' + dirlist[dirlist[0][subcat]].length + ')</i>'; 
	if (subdir < dirlist[dirlist[0][subcat]].length -1){
		divcontent = divcontent +  ' &gt; <a href="#" onclick="swapdetails(' + subcat + ", " + (subdir +1 ) + ", 'contenttitle2', 'detalles');" + '">&nbsp;/' + dirlist[subcat_name][subdir +1] ;
	}
    document.getElementById(divtitulo).innerHTML = divcontent;

	document.title = 'Lista de imagenes >> ' + dirlist[0][subcat]  ;

	divcontent = '<ul>';
    showitem = 0;
    for ( var i = 0; i < imagelist[subcat_name].length; i++) {
		if (dirlist[subcat_name][subdir] == imagelist[subcat_name][i][0].substring(0, imagelist[subcat_name][i][0].lastIndexOf("/"))){
            console.log(subcat_name + '/' + imagelist[subcat_name][i][0]);
            infoline = '';
            infoplus = '';
            infostar = '';
            infotags = '';

            // agregar linea con fecha nueva al cambiar del mes:
            if (showitem == 0 || imagelist[subcat_name][i][3] > imagelist[subcat_name][i-1][3]) {
                divcontent = divcontent + '</ul><span class="monthbreak"> ' + imagelist[subcat_name][i][1] + '</span> <ul>';
                showitem += 1;
            } 
            
            if ((subcat_name + '/' + imagelist[subcat_name][i][0]) in placetags) { 
                infoline = placetags[subcat_name + '/' + imagelist[subcat_name][i][0]][1];
                //if (infoline.indexOf("/") == 0) { 
                if ( /^[*#/]/.test(infoline) ) { 
                    infoplus = infoline;
                    //alert (infoplus);       // star, tag(s), info text (not place)
                } else {
                    divcontent = divcontent + '</ul><span class="tagbreak"> ' + infoline + '</span> <ul>';
                }
            }

            // atencion solo link apunta a thumbnail, ya no apunta al original !!
			//divcontent = divcontent + '<li><img id="lafoto' + i + '" src="' + subcat_name + '_th/' + imagelist[subcat_name][i][0] +'" width="120"><ul><li><a href="' + subcat_name + '_th/' + imagelist[subcat_name][i][0] + '" target="_blank" ><img id="lafoto_big' + i + '" src="' + subcat_name + '_th/' + imagelist[subcat_name][i][0] +'"></a></li></ul></li>';
			//divcontent = divcontent + '<li><img id="lafoto' + i + '" src="' + subcat_name + '_th/' + imagelist[subcat_name][i][0] +'" width="120"><ul><li><img id="lafoto_big' + i + '" src="' + subcat_name + '_th/' + imagelist[subcat_name][i][0] +'">' + imagelist[subcat_name][i][1] + '<br>' + imagelist[subcat_name][i][0].substring(imagelist[subcat_name][i][0].lastIndexOf("/") + 1) +  ' ' + imagelist[subcat_name][i][2] +'</li></ul></li>';
			divcontent = divcontent + '<li><img id="lafoto' + i + '" src="' + subcat_name + '_th/' + imagelist[subcat_name][i][0] +'" width="120"><ul><li><a href="#" onclick="return copy2box(\\'' + subcat_name  + '/' + imagelist[subcat_name][i][0] + ','+ imagelist[subcat_name][i][1] + '\\');"><img id="lafoto_big' + i + '" src="' + subcat_name + '_th/' + imagelist[subcat_name][i][0] +'"></a>' + imagelist[subcat_name][i][1] + '<br>' + imagelist[subcat_name][i][0].substring(imagelist[subcat_name][i][0].lastIndexOf("/") + 1) +  ' ' + imagelist[subcat_name][i][2] + infoplus + '</li></ul></li>';
		}
	}
    
	divcontent = divcontent + '</ul>';
	document.getElementById(divdetail).innerHTML = divcontent;

	return 0;
}


function copy2clip(thistext) {
    /* thanks 
    https://hackernoon.com/copying-text-to-clipboard-with-javascript-df4d4988697f
    https://gist.github.com/Chalarangelo/99e7cbee0de3c94f0077bb7555110767#file-copytoclipboard-js
    https://www.w3schools.com/howto/howto_js_copy_clipboard.asp
    */
    if (thistext === undefined) { thistext = '';} 
    
  const el = document.createElement('textarea');
  /* el.value = 'hola que tal'; */
  el.value = thistext;
  el.setAttribute('readonly', '');
  el.style.position = 'absolute';
  el.style.left = '-9999px';
  document.body.appendChild(el);
  el.select();
  document.execCommand('copy');
  
  //alert("Texto copiado: " + el.value);
  document.body.removeChild(el);

}



function copy2box(thistext) {
    if (thistext === undefined) { thistext = '';} 
    var taginfo = prompt("Info de " + thistext.split(",")[0], "Lugar, evento");
    if (taginfo) {
    
      document.getElementById("taglist").value += "\\n\\"" + thistext.split(",")[0] + "\\":\\t[\\"" + thistext.split(",")[1] + "\\", \\"" + taginfo + "\\"],";
      document.getElementById("taglist").value = document.getElementById("taglist").value.split("\\n").slice(0,14).join("\\n") + "\\n" + document.getElementById("taglist").value.split("\\n").slice(14).sort().join("\\n");

      document.getElementById("copylist").value += "\\n" + thistext.split(",")[0];
      document.getElementById("copylist").value = document.getElementById("copylist").value.split("\\n").sort().join("\\n");

      copyitems += 1;
      document.getElementById('copyicons').innerHTML = 'exportar <a href="#" onclick="copybox2clip(\\'taglist\\')">marcadores</a> <a href="#" onclick="copybox2clip(\\'copylist\\', \\'archivos.txt\\')">archivos</a> (' + copyitems + ')';
    }
    return false;
}


function copybox2clip(boxname, filename='placetags.js') {

  const el = document.getElementById(boxname);

  el.select();
  document.execCommand('copy');
  
  //alert("Save copied text to: " + filename);
  alert("Texto copiado para guardar en: " + filename);

}

// -->
</script>
</head>

<body onload="listas2menu(dirlist);">

<div id="menucategory" style="float: left; margin-right: 15pt;z-index:1000;"></div>
<div id="copyicons" style="float: right; margin-right: 15pt;z-index:1000;">..</div>

<center><div id="contenttitle2" >categoria actual</div></center>

<div id= "detalles" style="text-align: center;"></div>


<div id="taglistdiv" style="position: absolute; left: -9999px"><textarea id="taglist">
/*
Lista para guardar en marcadores - para destacar en pantalla del catalogo:

Save as: placetags.js

and in index_th.js comment: 
//placetags = [];

and uncomment: 
jsinclude('placetags.js');
*/

placetags = {
};
</textarea></div>

<div id="copylistdiv" style="position: absolute; left: -9999px"><textarea id="copylist">
    Lista de archivos a copiar</textarea></div>

</body>
</html>
"""
    
    if not os.path.exists(indexfile):
        idx = open(indexfile, 'w')
        idx.write(htmlcontent)
        idx.close()

    return 0


def dirscan(startdir, actiontype, targetdir, listfile_name, subdir, dive = 1):
    """
    objetivo: recorrer directorio y subdirectorios, y realizar acciones de acuerdo al tipo de archivos encontrados
    """
    itemsfound = 0
    #def dirwalkndo(startdir, actiontype, targetdir, validfiles, listfile, dive = 1, flatten = 0):
    #procesado = dirwalkndo(srcdir, 'jpgthums', targetdir, ['.jpg'], out_file, crawldirs, flattentargetdirs)
    #print "%d archivos procesados" % (procesado)

    validdirs = []
    otherfileslist = []
    #indexfile = 'imglist.js'


    skipdirs = ['.', '..']
    thumbwidth = 400
    if actiontype in ['jpgthumbs', 'jpglist', 'jpglistinfo', 'resize']:
        validfiles = ['.jpg']
        otherfiles = ['.avi', '.mp4', '.mov', '.raw', '.rw2']   # archivos a mencionar/listar, pero no convertir
        skipdirs = ['_', '.', '..', '_inf', '_thumbs', '.svn']
        infofiles = ['.txt', '.nfo', '.tag']
    elif actiontype in ['clonetree', 'synctree']:
        validfiles = ['.jpg']
        otherfiles = ['.mp5', '.rw8']
        skipdirs = ['_', '.', '..', '_inf', '_thumbs', '.svn']
        infofiles = ['.txt', '.nfo', '.tag']
    else: 
        return -100
        
    if actiontype == 'resize':
        _usage = """ Opciones de dimension:
640, 800, 1024, 2048, 3072
"""
        print (_usage)
        #uchoose= int(raw_input("Ingrese la opcion: "))
        size_choose = int(raw_input("Escriba el numero: ")[:1])
        if size_choose > 7:
            thumbwidth = 800
        if size_choose > 4:
            thumbwidth = 640
        elif size_choose > 0:
            thumbwidth = size_choose * 1024
        print ("targetdir: %s" % (targetdir))
        #sys.exit()

    if actiontype in ['jpgthumbs', 'clonetree', 'resize', 'synctree']:
        if not os.path.exists(targetdir):
            os.mkdir(targetdir)
    # eventualmente agregar fecha, o algun numero diferenciador..
    
    if actiontype in ['jpgthumbs', 'jpglist', 'jpglistinfo']:
        listfile = open(listfile_name, 'w')
            
        # out_file: header
        headertext = """// sdcat (kh) ver %s - listado %s
generated['%s'] = "%s";
listfile_master['%s'] = "index_th.js";
thumb_root['%s'] = "%s_th";
orig_root['%s'] = "%s";

imagelist['%s'] = [
""" # caso windows - orig_absroot = "file:///E:/DCIM/100RICOH";
        # caso originales en directorio "al lado", sobreescribir variable javascript
        listfile.write(headertext % (app_ver, time.strftime("%Y%m%d_%H%M"), subdir, time.strftime("%d/%m/%Y %H:%M"), subdir, subdir, subdir + '_th', subdir, subdir, subdir))

        #listfile.write('imagelist = [\n')

    currdir = ''
    for root, dirs, files in os.walk(startdir):
        files.sort()

        if os.path.split(root)[1] in skipdirs:
            # what about subdirs of skipdirs ??
            continue
            
        thumb_dir = os.path.join(targetdir, root[len(startdir)+1:])
        
        if actiontype in ['clonetree', 'synctree']:
            mk_dir(thumb_dir)
            # solo un nivel, esta mas completo en img_thumb !!
            #if not os.path.exists(thumb_dir):
            #    os.mkdir(thumb_dir)
            if actiontype == 'clonetree':
                continue


        for f in files:

            if os.path.splitext(f)[1].lower() in validfiles:
                itemsfound += 1
                #print os.path.join(root,f)
                thisfile = os.path.join(root,f)

                if actiontype in ['jpgthumbs', 'resize'] :
                    # verificar/crear thumbdir, verificar thumb in base-mover/verificar eliminar thumb incorrecto existente - crear thumb
                    #img_thumb(srcfile, os.path.join(target_dir,f), thumbwidth)
                    mk_dir(thumb_dir)
                    if actiontype == 'resize':
                        img_thumb(os.path.join(root,f), os.path.join(thumb_dir, os.path.splitext(f)[0] + '_' + str(thumbwidth) + os.path.splitext(f)[1]), thumbwidth)
                    elif actiontype == 'jpgthumbs':
                        img_thumb(os.path.join(root,f), os.path.join(thumb_dir,f), thumbwidth)
                    # .. opcion de listar only ??
                    
                   
                if actiontype in ['jpgthumbs', 'jpglist', 'jpglistinfo']:
                    # write out index
                    #listfile.write("\"%s\",\n" % os.path.join(root[len(startdir)+1:],f).replace('\\', '/').replace('//', '/') )
                    #listfile.write("[\"%s\", \"%s\", \"%s\"],\n" % (os.path.join(root[len(startdir)+1:],f).replace('\\', '/').replace('//', '/'), str(time.strftime("%d/%m/%Y %H:%M:%S",time.gmtime(os.path.getmtime(os.path.join(root,f))))), img_size(os.path.join(root,f)) ))
                    # format: filename, date, dimensions, yyyymm - group, stars, tags
                    #listfile.write("[\"%s\", \"%s\", \"%s\", \"%s\", \"\", \"\"],\n" % (os.path.join(root[len(startdir)+1:],f).replace('\\', '/').replace('//', '/'), str(time.strftime("%d/%m/%Y %H:%M:%S",time.gmtime(os.path.getmtime(os.path.join(root,f))))), img_size(os.path.join(root,f)), str(time.strftime("%Y%m",time.gmtime(os.path.getmtime(os.path.join(root,f))))) ))
                    
                    if os.path.exists(os.path.join(root,f)):
                        thisimage = Image.open(os.path.join(root,f))
                    #print thisfile

                    listfile.write("[\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"\"],\n" % (os.path.join(root[len(startdir)+1:],f).replace('\\', '/').replace('//', '/'), str(time.strftime("%d/%m/%Y %H:%M:%S",time.gmtime(os.path.getmtime(thisfile)))), img_size(thisfile), str(time.strftime("%Y%m",time.gmtime(os.path.getmtime(thisfile)))), img_getexif(thisimage, 'Model'), img_getexif(thisfile, 'LensSpecification'), img_getexif(thisimage, 'FocalLength'), img_getexif(thisimage, 'ISOSpeedRatings'), img_getexif(thisimage, 'FNumber'), img_getexif(thisimage, 'ExposureTime')))
                    #print ("[\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"\"]," % (os.path.join(root[len(startdir)+1:],f).replace('\\', '/').replace('//', '/'), str(time.strftime("%d/%m/%Y %H:%M:%S",time.gmtime(os.path.getmtime(thisfile)))), img_size(thisfile), str(time.strftime("%Y%m",time.gmtime(os.path.getmtime(thisfile)))), img_getexif(thisimage, 'Model'), img_getexif(thisfile, 'LensSpecification'), img_getexif(thisimage, 'FocalLength'), img_getexif(thisimage, 'ISOSpeedRatings'), img_getexif(thisimage, 'FNumber'), img_getexif(thisimage, 'ExposureTime')))
                    #outfile.write(ff+'\t'+ string.upper(ff[ff.rfind(".")+1:])+'\t'+ str(os.path.getsize(file))+'\t'+ str(time.strftime("%d/%m/%Y %H:%M:%S",time.gmtime(os.path.getmtime(file))))+'\t'+ os.path.split(path)[1]+'\n')


                if root != currdir:
                    currdir = root
                    validdirs.append(root[len(startdir)+1:].replace('\\', '/').replace('//', '/'))

            elif os.path.splitext(f)[1].lower() in otherfiles:
                print (f)
                # listar adicional en otra variable
                otherfileslist.append(os.path.join(root,f))
                
            if (os.path.splitext(f)[1].lower() in infofiles and actiontype == 'jpglistinfo') or actiontype == 'synctree':
                if not os.path.exists(thumb_dir):
                    mk_dir(thumb_dir)
                   
                #if not os.path.exists(os.path.join(thumb_dir,f)) or actiontype == 'jpglistinfo':
                if not os.path.exists(os.path.join(thumb_dir,f)) or not samefiles(os.path.join(root,f), os.path.join(thumb_dir,f)) or actiontype == 'jpglistinfo':
                    print "copiando", f
                    shutil.copy2(os.path.join(root,f), os.path.join(thumb_dir,f))       # copiar sin preguntar
                        #shutil.move(os.path.join(os.path.split(target_dir)[0], os.path.split(imgout)[1]), imgout)
                else:
                    print '.',   


    if actiontype in ['jpgthumbs', 'jpglist']:
        listfile.write('];\n\n')

        validdirs.sort()
        listfile.write("dirlist['%s'] = %s;\n\n" % (subdir, validdirs))
        
        otherfileslist.sort()
        listfile.write("otherfiles['%s'] = %s;" % (subdir, otherfileslist))

        listfile.close()
    
    return itemsfound


def main(args):
    """
    objetivo: menu del programa y ciclo de operacion global
    """

    global app_ver
    app_ver = '0.0.1709'


    # menu inicial - modos de operacion
    print "programa de catalogar imagenes"

    Tkinter.Tk().withdraw() # Close the root window

    #dir_start = os.path.abspath(os.curdir)
    #dir_start = dir_target
    # .. dir_start puede ser uno que se le indica
    if len(sys.argv) > 1: 
        dir_start = sys.argv[1]

    else:
        dir_start = tkFileDialog.askdirectory(initialdir=os.curdir, title='Seleccione directorio base (DCIM) de ORIGEN')
        #directory = os.path.dirname(os.path.realpath(tkFileDialog.askopenfilename()))
        #print(directory)
        if len(dir_start) < 1:
            #print "utilizando directorio inicial"
            if not tkMessageBox.askokcancel("Directorio base de origen","No se indicó ningun directorio. Desea utilizar el directorio de inicio ?"):
                sys.exit()
                #return -1
            dir_start = os.path.abspath(os.curdir)

    if not os.path.exists(dir_start):
        print ("%s no es un directorio valido" % (dir_start))
        #for _uu in _usage:
        #    print _uu
        sys.exit()

    print ("Iniciando scan en: %s" % (dir_start))

    #dir_target = os.path.abspath(os.curdir)
    dir_target = tkFileDialog.askdirectory(initialdir=os.curdir, title='Seleccione directorio DESTINO o escriba el nombre del nuevo directorio para crearlo')
    #directory = os.path.dirname(os.path.realpath(tkFileDialog.askopenfilename()))
    #print(directory)
    # sugerir directorio base actual u otro basado en feche (actual o de imagenes encontradas) y/o tipo unidad SD/HD de origen ?
    if len(dir_target) < 1:
        #print "utilizando directorio inicial"
        if not tkMessageBox.askokcancel("Directorio base destino","No se indicó ningun directorio. Desea utilizar el directorio de inicio ?"):
            sys.exit()
            #return -1
        dir_target = os.path.abspath(os.curdir)
    if not os.path.exists(dir_target):
        print ("creando directorio nuevo.." + dir_target)
        os.makedirs(dir_target)
    print ("Destino: %s" % (dir_target))
    #return -2



    _usage = """ Operaciones:
    J - listado de imagenes JPG y miniaturas
    L - solo Listado de imagenes JPG
    i - listado de imagenes JPG + copia de archivos INFO (.txt, .inf, .nfo, .tag, .hot)
    S - Syncronizar todos los archivos arbol origen al arbol destino ***
    C - Clonar arbol vacio de (sub)-directorios
    R - Redimensionar imagenes JPG del directorio inicial
    .. elija la LETRA deseada
    """
    print (_usage)
    #uchoose= int(raw_input("Ingrese la opcion: "))
    uchoose = string.upper(raw_input("Ingrese la opcion: ")[:1])
    #uchoose = 1
    uoptions = {'J':'jpgthumbs', 'L':'jpglist', 'I':'jpglistinfo', 'C':'clonetree', 'S':'synctree', 'R':'resize'}
    if not uchoose in uoptions:
        print ("opcion seleccionada no valida")
        sys.exit()
    #if uoptions[uchoose]=='dironly':
    
    if uoptions[uchoose] == 'resize':
        matchitems = dirscan(dir_start, uoptions[uchoose], dir_target, os.path.join(dir_target, 'reduce.txt'), 'resize')
        sys.exit()

    if uoptions[uchoose] in ['clonetree', 'synctree']:
        matchitems = dirscan(dir_start, uoptions[uchoose], dir_target, os.path.join(dir_target, 'dirtree.txt'), uoptions[uchoose])
        sys.exit()
        

    # preparation for my personal local static web page ;) - no need for php..
    indexfile = 'imglist.js'
    index2file = 'index2.js'

    """
    d='.'
    ll = [os.path.join(d,o) for o in os.listdir(d) if os.path.isdir(os.path.join(d,o))]
    print ll
    
    """
    matchcount = 0
    matchdirs = []
    for sdir in next(os.walk(dir_start))[1]:
        print (sdir)
        if (re.match('^([1-9][0-9]{2}).{1,5}$', sdir) and not re.match('.*_th$', sdir)):
            # DCIM pattern: 123ABCDE = 3 numeros + hasta 5 caracteres
            matchcount += 1

            targetdir = os.path.join(dir_target, os.path.split(sdir)[1] + '_th')
            if len(sys.argv) > 2: 
                targetdir = os.path.join(sys.argv[2], os.path.split(sdir)[1] + '_th')
                # .. check if sys.argv[2] is valid target base dir
            #print "Clonando desde %s a %s" % (sdir, targetdir)

            if do_beep > 0:
                os.system("beep -f 555 -l 100")
            #print "Generando listado de indice en: %s" % (os.path.join(targetdir,indexfile))
            print ("Generando listado de indice en: %s" % (os.path.join(dir_target, sdir + '_th.js')))
            if len(sys.argv) < 2: 
                if raw_input( "Listo para proceder - o saltar ? (y/n)>" )[:1] in 'nN' :
                    #sys.exit()     
                    continue
                    # .. not exit, just skip this sdir

                #if os.path.exists( os.path.join(targetdir,indexfile)):
                if os.path.exists( os.path.join(dir_target, sdir + '_th.js')):
                    if raw_input( "Archivo ya existe, sobreescribir (y) - o omitir (n) ? (y/n)>" )[:1] in 'nN' :
                        #sys.exit()       # check valid entry
                        continue
                        # .. not exit, just skip this sdir

            # procesar...
            #if actiontype == 'jpgthumbs':
            #    if not os.path.exists(targetdir):
            #        print ("creando %s" % (targetdir))
            #        os.mkdir(targetdir)
            #        # .. try - error

            
            #out_file_name = os.path.join(dir_target, sdir + '_th.js')
                    
            # do: create mirror thumb, out_file: detect infos 
            #matchitems = dirscan(os.path.join(dir_start, sdir), uoptions[uchoose], targetdir, out_file)
            matchitems = dirscan(os.path.join(dir_start, sdir), uoptions[uchoose], targetdir, os.path.join(dir_target, sdir + '_th.js'), sdir)
            

            if matchitems > 0:
                matchdirs.append(sdir)
            else:
                print ("nada encontrado en " + sdir)
                # eliminar out_file ?? o incluir TODOS los sdirs en index_th.js indicando items procesados ?

        else:
            print ("-") #"--ignorando."

    print (matchdirs)

    if uoptions[uchoose] in ['jpgthumbs', 'jpglist', 'jpglistinfo']:
        
        index_file = open(os.path.join(dir_target, 'index_th.js'), 'w')
        matchdirs.sort()

        indexheader = """// sdcat (kh) ver %s - listado %s
//Indice general
listfile_master = [];
listfile_master[0] = "index_th.js";
generated = [];
generated[0] = "%s";

// http://chapter31.com/2006/12/07/including-js-files-from-within-js-files/
function jsinclude(file)
{
  var script  = document.createElement('script');
  script.src  = file;
  script.type = 'text/javascript';
  script.defer = true;
  document.getElementsByTagName('head').item(0).appendChild(script);
}
// jsinclude('js/myFile1.js');

//indice de subdirectorios de thumbs con archivos de imagenes";
dirlist = [];
dirlist[0] = %s;

imagelist = [];
otherfiles = [];

placetags = [];

"""
        if not os.path.exists(os.path.join(dir_target, 'placetags.js')):
            indexheader += "//"
        indexheader += """jsinclude('placetags.js');
        
"""
        
        # caso windows - orig_absroot = "file:///E:/DCIM/100RICOH";
        index_file.write(indexheader % (app_ver, time.strftime("%Y%m%d_%H%M"), time.strftime("%d/%m/%Y %H:%M"), matchdirs))
        indexline = """jsinclude('%s_th.js');
"""
        for matchdir in matchdirs:
            index_file.write(indexline % (matchdir))
            
        index_file.close()

        if do_beep > 0:
            os.system("beep -f 555 -l 100")

        if not os.path.exists(os.path.join(dir_target, 'index.html')):
            if raw_input( "Archivo index no existe, desea crearlo ? (y/n)>" )[:1] in 'yY' :
                print ("creando archivo index...")
                create_index(os.path.join(dir_target, 'index.html'))

    if matchcount < 1:
        print ("directorio DCIM no encontrado, favor indicar otro directorio de origen")


        
    #print ("..fin")
    print ("FIN scan desde: %s a: %s" % (dir_start, dir_target))
    
    return 0


if __name__ == '__main__':
    # import sys
    sys.exit(main(sys.argv))
