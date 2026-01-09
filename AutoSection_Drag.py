import ezdxf
import math
import os
import sys
from shapely.geometry import LineString, MultiPolygon, Polygon, box
from shapely.ops import unary_union

def process_logic(input_path):
    output_path = input_path.replace(".dxf", "_填充完成.dxf")
    doc = ezdxf.readfile(input_path)
    msp = doc.modelspace()

    raw_geoms = []
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')

    # 1. 提取几何边界
    for ent in msp:
        if ent.dxftype() in ('LINE', 'LWPOLYLINE', 'POLYLINE'):
            try:
                if ent.dxftype() == 'LINE':
                    geom = LineString([ent.dxf.start.vec2, ent.dxf.end.vec2])
                else:
                    pts = [p[:2] for p in ent.get_points()] if ent.dxftype() == 'LWPOLYLINE' else [p.vtx.vec2 for p in ent.vertices]
                    if len(pts) < 2: continue
                    geom = LineString(pts)
                raw_geoms.append(geom)
                x1, y1, x2, y2 = geom.bounds
                min_x, min_y, max_x, max_y = min(min_x, x1), min(min_y, y1), max(max_x, x2), max(max_y, y2)
            except: continue

    # 2. 拓扑计算（确保面积完整，不处理文字孔洞）
    thick_walls = [line.buffer(0.2, cap_style=2, join_style=2) for line in raw_geoms]
    combined_walls = unary_union(thick_walls)
    spaces = box(min_x-10, min_y-10, max_x+10, max_y+10).difference(combined_walls)
    
    valid_regions = []
    if isinstance(spaces, Polygon): valid_regions.append(spaces)
    elif isinstance(spaces, MultiPolygon): valid_regions.extend(list(spaces.geoms))
    valid_regions = sorted(valid_regions, key=lambda p: p.area, reverse=True)[1:]

    # 3. 生成填充
    if "AA_填充层" not in doc.layers: doc.layers.add("AA_填充层", color=7)
    rgb_list = [(255,150,150), (150,255,150), (150,150,255), (255,255,100), (255,100,255), (100,255,255)]
    patterns = ['ANSI31', 'ANSI32', 'ANSI33']
    
    count = 0
    for i, poly in enumerate(valid_regions):
        if poly.area < 1.0: continue
        outer_poly = poly.buffer(-0.05, join_style=2).simplify(0.01)
        try:
            diag = math.sqrt((outer_poly.bounds[2]-outer_poly.bounds[0])**2 + (outer_poly.bounds[3]-outer_poly.bounds[1])**2)
            hatch = msp.add_hatch(dxfattribs={'layer': 'AA_填充层'})
            hatch.rgb = rgb_list[i % len(rgb_list)]
            hatch.set_pattern_fill(patterns[i%3], scale=max(2.0, diag*0.2))
            hatch.paths.add_polyline_path(list(outer_poly.exterior.coords)[:-1], is_closed=True)
            for interior in outer_poly.interiors:
                hatch.paths.add_polyline_path(list(interior.coords)[:-1], is_closed=True)
            count += 1
        except: continue

    doc.saveas(output_path)
    return output_path, count

if __name__ == "__main__":
    # 获取拖拽进来的文件路径
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if file_path.lower().endswith('.dxf'):
            print(f"正在处理: {file_path}")
            try:
                out, num = process_logic(file_path)
                print(f"成功！生成 {num} 个区域。")
                print(f"保存至: {out}")
            except Exception as e:
                print(f"处理失败: {e}")
        else:
            print("请拖入一个 .dxf 文件！")
    else:
        print("使用方法：将 DXF 文件直接拖动到此 EXE 图标上。")
    
    input("\n处理结束，按回车键退出...")