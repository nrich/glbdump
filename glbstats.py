#!/usr/bin/env python
# https://github.com/KhronosGroup/glTF/tree/master/specification/2.0#glb-file-format-specification
import sys, json, os
from struct import unpack

stats = os.stat(sys.argv[1])
f = open(sys.argv[1], 'rb')

if f.read(4) != b'glTF':
    print("This doesn't appear to be a Binary glTF file!")
    sys.exit(-1)
    
container_version = unpack('<I', f.read(4))[0]
if container_version != 2:
    print("Don't know how to handle container version %d, only know 2" % container_version)
    sys.exit(-1)
    
length = unpack('<I', f.read(4))[0]
print('Total file size %s bytes' % format(length, ',d'))
if stats.st_size != length:
    print('Warning: file size in .glb does not match actual file size (%s)!' % \
        format(stats.st_size, ',d'))

# Process JSON chunk
chunk_length = unpack('<I', f.read(4))[0]
chunk_type = f.read(4)
if chunk_type != b'JSON':
    print('First chunk is not of type JSON!')
    sys.exit(-1)

print()
print('JSON chunk (%s bytes)' % format(chunk_length, ',d'))

js = f.read(chunk_length).decode('utf8')
j = json.loads(js)

f.close()

buffers = j['buffers']
bufferviews = j['bufferViews']
accessors = j['accessors']

print('Asset version %s' % j['asset']['version'])
print('Asset generator "%s"' % j['asset']['generator'])
if j['asset']['version'] != '2.0':
    print('Warning: not sure if we understand version != 2.0, but continuing anyway')

print()
print('Elements:')
print('%4d nodes' % len(j['nodes']))
print('%4d cameras' % len(j['cameras']))
totalimsize = 0
for i in j['images']:
    totalimsize += bufferviews[i['bufferView']]['byteLength']
print('%4d images     (total %s bytes)' % (len(j['images']), format(totalimsize, ',d')))
print('%4d materials' % len(j['materials']))
print('%4d meshes' % len(j['meshes']))
print('%4d textures' % len(j['textures']))
print()

totalbufsize = 0
for b in buffers:
    totalbufsize += b['byteLength']
print('%4d buffers    (total %s bytes)' % (len(buffers), format(totalbufsize, ',d')))

totalaccsize = 0
for a in accessors:
    totalaccsize += bufferviews[a['bufferView']]['byteLength']
print('%4d accessors  (total %s bytes)' % (len(accessors), format(totalaccsize, ',d')))

print()
print('Images:')
for idx, i in enumerate(j['images']):
    bv = i['bufferView']
    length = bufferviews[bv]['byteLength']
    print('[%4d] %11s bytes  %-12s "%s"' % (idx, format(length,',d'), i['mimeType'], i['name']))
    
print()
print('Meshes:')
for idx, m in enumerate(j['meshes']):
    vertices = 0
    normals = 0
    color0 = 0
    texcoord0 = 0
    texcoord1 = 0
    indices = 0
    for p in m['primitives']:
        attrs = p['attributes']
        vertices += accessors[attrs['POSITION']]['count']
        if 'NORMAL' in attrs:
            normals += accessors[attrs['NORMAL']]['count']
        if 'COLOR_0' in attrs:
            color0 += accessors[attrs['COLOR_0']]['count']
        if 'TEXCOORD_0' in attrs:
            texcoord0 += accessors[attrs['TEXCOORD_0']]['count']
        if 'TEXCOORD_1' in attrs:
            texcoord1 += accessors[attrs['TEXCOORD_1']]['count']
        indices += accessors[p['indices']]['count']
        
    s = '[%4d] %-30s  %4dP %8sV %8sI' % \
        (idx, '"'+m['name']+'"', len(m['primitives']), format(vertices, ',d'), format(indices, ',d'))
    
    if color0 > 0:
        s += ' %8sC0' % format(color0, ',d')
    if normals > 0:
        s += ' %8sN' % format(normals, ',d')
    if texcoord0 > 0:
        s += ' %8sT0' % format(texcoord0, ',d')
    if texcoord1 > 0:
        s += ' %8sT1' % format(texcoord1, ',d')
        
    print(s)

print()
print('Materials:')
for idx, m in enumerate(j['materials']):
    print('[%4d] "%s"' % (idx, m['name']))

print()
print('Buffers:')
for idx, b in enumerate(buffers):
    print('[%4d] %11s bytes' % (idx, format(b['byteLength'], ',d')))
    

component_types = {
    5120: 'BYTE', 5121: 'UNSIGNED_BYTE', 5122: 'SHORT', 5123: 'UNSIGNED_SHORT', 
    5125: 'UNSIGNED_INT', 5126: 'FLOAT'
}
    
print()
print('Accessors:')
for idx, a in enumerate(accessors):
    bytelength = bufferviews[a['bufferView']]['byteLength']
    comptype = a['componentType']
    if comptype not in component_types:
        comptype = '??? (%d)' % comptype
    else:
        comptype = component_types[comptype]
    print('[%4d] %8sx  %-6s  %-14s  %11s bytes' % \
        (idx, format(a['count'], ',d'), a['type'], comptype, format(bytelength, ',d')))


print()