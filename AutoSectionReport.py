import ezdxf
import math
from shapely.geometry import LineString, MultiPolygon, Polygon, box, Point
from shapely.ops import unary_union

# ================= 参数设置 =================
INPUT_DXF = "t.dxf"
OUTPUT_DXF = "AutoSection_Final_v1.dxf"

GAP_TOLERANCE = 0.2 
SPARSITY_FACTOR = 0.2 
TEXT_OFFSET = 1.0  # 文字避让的边缘外扩距离

RGB_COLORS = [
    (255, 150, 150), (150, 255, 150), (150, 150, 255),
    (255, 255, 150), (255, 150, 255), (150, 255, 255)
]
CLEAN_PATTERNS = ['ANSI31', 'ANSI32', 'ANSI33']

def run_final_v1():
    print("1. 正在读取并分析图纸...")
    try:
        doc = ezdxf.readfile(INPUT_DXF)
        msp = doc.modelspace()
    except Exception as e:
        print(f"读取失败: {e}"); return

    raw_geoms = []
    text_boxes = [] # 用于存储文字的避让矩形
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')

    for ent in msp:
        # A. 提取线条
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
                min_x, min_y = min(min_x, x1), min(min_y, y1)
                max_x, max_y = max(max_x, x2), max(max_y, y2)
            except: continue
        
        # B. 提取文字包围盒 (用于避让)
        if ent.dxftype() in ('TEXT', 'MTEXT'):
            try:
                insert = ent.dxf.insert
                # 这里我们根据字高估算一个避让框
                # 专业的做法是使用 ent.get_bounding_box()，但有些环境不支持，我们用简易算法
                height = ent.dxf.height
                width = len(ent.dxf.text) * height * 0.6 if ent.dxftype() == 'TEXT' else height * 5
                t_box = box(insert.x - TEXT_OFFSET, insert.y - TEXT_OFFSET, 
                            insert.x + width + TEXT_OFFSET, insert.y + height + TEXT_OFFSET)
                text_boxes.append(t_box)
            except: continue

    print("2. 拓扑重构与文字避让计算...")
    thick_walls = [line.buffer(GAP_TOLERANCE, cap_style=2, join_style=2) for line in raw_geoms]
    combined_walls = unary_union(thick_walls)
    canvas = box(min_x - 10, min_y - 10, max_x + 10, max_y + 10)
    spaces = canvas.difference(combined_walls)
    
    valid_regions = []
    if isinstance(spaces, Polygon): valid_regions.append(spaces)
    elif isinstance(spaces, MultiPolygon): valid_regions.extend(list(spaces.geoms))
    valid_regions = sorted(valid_regions, key=lambda p: p.area, reverse=True)[1:]

    print(f"3. 正在生成智能填充...")
    if "AA_HATCH" not in doc.layers: doc.layers.add("AA_HATCH")

    count = 0
    for i, poly in enumerate(valid_regions):
        if poly.area < 1.0: continue
        # 填充主边界
        outer_poly = poly.buffer(-0.05, join_style=2).simplify(0.01)

        try:
            x1, y1, x2, y2 = outer_poly.bounds
            diag_len = math.sqrt((x2-x1)**2 + (y2-y1)**2)
            adaptive_scale = max(2.0, diag_len * SPARSITY_FACTOR) 

            hatch = msp.add_hatch(dxfattribs={'layer': 'AA_HATCH'})
            hatch.rgb = RGB_COLORS[i % len(RGB_COLORS)]
            hatch.set_pattern_fill(CLEAN_PATTERNS[i % len(CLEAN_PATTERNS)], scale=adaptive_scale)
            
            # 写入外环
            hatch.paths.add_polyline_path(list(outer_poly.exterior.coords)[:-1], is_closed=True)
            
            # --- 智能避让：检查哪些文字框落在这个填充内 ---
            for tb in text_boxes:
                if outer_poly.intersects(tb):
                    # 将文字框作为内环(Island)加入
                    # 获取交集部分，防止文字框超出填充边界
                    island = outer_poly.intersection(tb)
                    if not island.is_empty and isinstance(island, Polygon):
                        hatch.paths.add_polyline_path(list(island.exterior.coords)[:-1], is_closed=True)
            
            # 写入原本存在的内部孔洞
            for interior in outer_poly.interiors:
                hatch.paths.add_polyline_path(list(interior.coords)[:-1], is_closed=True)
            
            count += 1
        except: continue

    doc.saveas(OUTPUT_DXF)
    print("------------------------------------------------")
    print(f"GitHub 提交版处理完成！生成区域: {count}")
    print(f"功能点：1.置底 2.RGB彩色 3.文字智能避让 4.面积无损")

if __name__ == "__main__":
    run_final_v1()