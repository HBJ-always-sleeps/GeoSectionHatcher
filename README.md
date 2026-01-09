# GeoSectionHatcher
GeoSectionHatcher is an automated hatching tool specifically designed for geological cross-section drawings in AutoCAD. Utilizing topology reconstruction algorithms, it automatically identifies boundary gaps and performs intelligent, multi-colored hatching with a single action.

Key Features
Drag-and-Drop Workflow: No Python environment required. Simply drag DXF files onto the EXE icon to start processing.

Intelligent Topology Closure: Automatically handles minor gaps in geological linework, solving the common "boundary not closed" issue in native CAD commands.

100% Area Accuracy: Hatch patterns use complete geometric boundaries without "cut-outs" for text, ensuring strictly accurate volume/area statistics for engineering reports.

Adaptive Visual Optimization: Automatically adjusts hatch scales based on the area size and applies random RGB colors to distinguish different soil layers.

How to Use
Download the latest 断面地质填充工具_拖拽版.exe from the Releases page.

Select one or multiple .dxf files that need processing.

Drag and drop them onto the exe icon.

A new file named Filename_填充完成.dxf will be generated in the same directory upon completion.

Developer Info
Language: Python 3.x

中文说明
简介
GeoSectionHatcher 是一款专为地质工程师设计的 AutoCAD 断面图自动填充工具。它利用拓扑重构算法，能够自动识别并不十分严密的线条边界，实现一键智能化彩色填充。

核心功能
拖拽式极简操作：无需安装 Python 环境，直接将 DXF 文件拖动到 EXE 图标上即可完成处理。

智能拓扑闭合：自动处理地质线条中微小的间隙（Gap Tolerance），解决原生 CAD 填充命令无法闭合的痛点。

100% 面积无损：填充图案采用完整几何边界，不会因为文字避让而产生面积误差，确保工程方量统计严格准确。

自适应视觉优化：根据闭合区域大小自动调整填充比例，并采用随机 RGB 色彩区分不同土层。

使用方法
从 Releases 页面下载最新版本的 断面地质填充工具_拖拽版.exe。

选中一个或多个需要处理的 .dxf 文件。

将其拖动并放置在 exe 文件图标上。

程序运行完成后，将在同级目录下生成名为 文件名_填充完成.dxf 的新文件。

开发者说明
语言：Python 3.x

核心库：ezdxf (CAD处理), shapely (几何运算)

打包建议：建议使用 pyinstaller --onefile 进行打包，以获得最佳的兼容性。
Core Libraries: ezdxf (CAD Processing), shapely (Geometric Operations)

Building: It is recommended to use pyinstaller --onefile for the best distribution compatibility.
