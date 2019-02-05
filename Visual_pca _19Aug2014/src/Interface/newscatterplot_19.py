'''
Created on 11/06/2013

@author: sob016
'''


"""
Draws several overlapping scatter plots.

Left-drag pans the plot.

Right-drag in the X(Y) direction zooms the plot in and out in X(Y) direction.

Mousewheel up and down zooms the plot in and out.

Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular region to
zoom.  

Left double clicking activates the polygon selection tool 

"""

from numpy import var
import numpy as np
import colorsys

# ETS imports (non-chaco)
from enable.component_editor import ComponentEditor
from traits.api import HasTraits, Instance, Int, Float, List, Str, Enum , Button 
from traitsui.api import Item, View, HSplit, VGroup, EnumEditor, VSplit, TableEditor, ObjectColumn, HGroup, ButtonEditor


# Chaco and matplotlib imports
from chaco.tools.line_segment_tool import LineSegmentTool
from chaco.api import ArrayPlotData, Plot
from chaco.tools.api import PanTool, ZoomTool
from chaco.plot_factory import create_scatter_plot, add_default_grids, add_default_axes
from chaco.plot_containers import OverlayPlotContainer
from chaco.tools.drag_zoom import DragZoom
#import matplotlib.nxutils as nx
from matplotlib.path import Path




# Project packages import
from Business.util import  makeFakeArray, makeFakePCAArray, readPhenotypesFromCSVFile, readPhenotypesFromCSVFile_pd
from DataAccess.PCA import PCA
from Business.pca_algurithm import PCA_Algorithm


shapes = ["square", "circle","inverted_triangle", "diamond", "dot", "cross", "plus", "pixel"]  
sizes = ["s1", "s2", "s3", "s4", "s5", "s6" ]

def loadPhenoTypeFromFile(fileName):
    # write 500,000 feature 30 sample
    pass

def getColor(color_str):        
    return int(color_str[1:7], 16)

def get_colors(num_colors):
        colors=[]
        for i in np.arange(0., 360., 360. / num_colors):
            hue = i/360.
            lightness = 0.5
            saturation = 1.0
            r,g,b = colorsys.hls_to_rgb(hue, lightness, saturation)
            colors.append("#%02X%02X%02X" % (r * 255, g * 255, b * 255))
        return colors

class MyData(HasTraits):
    PCA_Index=Int
    Percentage_Power=Float
    Cumulative_Percentage_Power=Float
    
class ShapeTable(HasTraits):
    pass
class ColorTable(HasTraits):
    pass      
class SizeTable(HasTraits):
    pass          
    
def validate_choice(value):
    if value == value.lower():
        return value
    else:
        raise ValueError('Must be lower case')   
    
               
class LineDrawer2D(LineSegmentTool):
    
    def setPCAData(self,plot, pcaData):
        self.plot = plot
        self.PCAData = pcaData
        
    def _finalize_selection(self):
        verts = np.array(self.points, float)
        
        path = Path(verts) 
    
        i = 1
        for batch in self.PCAData.batchs:
            i = i +1
            if (self.plot.active_scores_combobox == "Post Scores"):
                y1 = batch.postscores[int(self.plot.Y_PCA)]
                x1 = batch.postscores[int(self.plot.X_PCA)]                        
            else:
                x1 = batch.prescores[int(self.plot.X_PCA)]
                y1 = batch.prescores[int(self.plot.Y_PCA)]
                
            if path.contains_point([x1,y1])==1:
                batch.isSelected = True
            else:
                batch.isSelected = False
            
        self.plot._create_2D_plot()
        self.plot._create_1D1_plot()
        

class PlotApp2(HasTraits):
    numPcaScores = PCA.nums
    plotdata = Instance(ArrayPlotData)
    
    Y_PCA = Str
    YPCA = List(Str)
    
    X_PCA = Str
    XPCA = List(Str)
    
    Color = Str
    Colordropdownlist = List(Str)
    colors = List(str)
    
    Shape = Str
    Shapedropdownlist = List(Str)
    
    Size = Str
    Sizedropdownlist = List(Str)
    
    shapes_name = List(Str)
    colors_name = List(Str)
    sizes_name  = List(Str)
   
    active_scores_combobox = Enum(['Post Scores','Pre Scores'])
    start_selection = Button(label='Start Selection')
    stop_selection = Button(label='Stop Selection')
    export_selection = Button(label='export data')

    RightPlot = Instance(OverlayPlotContainer)
    LeftPlot = Instance(OverlayPlotContainer)

    button_editor = ButtonEditor()

    table = List(Instance(MyData))
    columns = [ObjectColumn(name='name')]
    columns.append(ObjectColumn(name="Value"))
    table_editor=TableEditor(columns=columns,
        deletable = True,
        sortable = False,
        sort_model = False,
        show_lines = True,
        line_color = "black",
        editable= False,
        show_column_labels = False)
    
    shape_table = List(Instance(ShapeTable))
    shape_columns = List(Instance(ObjectColumn))
    
    color_table = List(Instance(ColorTable))
    color_columns = List(Instance(ObjectColumn))
    
    size_table = List(Instance(SizeTable))
    size_columns = List(Instance(ObjectColumn))

        
    traits_view = View(
            VSplit(           
            HSplit(
                   VGroup(
                        VGroup(
                             Item('Y_PCA',                                 
                                editor=EnumEditor(
                                name='YPCA',
                                evaluate=validate_choice,
                                ),
                            ),
                            Item('X_PCA',                            
                                editor=EnumEditor(
                                name='XPCA',
                                evaluate=validate_choice,
                                ),
                            ),
                            Item('active_scores_combobox', width=225, label = "Score"),
                                HGroup(
                                     Item('start_selection', editor=button_editor, show_label=False, width=0.5),
                                     Item('stop_selection', editor=button_editor, show_label=False, width=0.5),
                                                                          
                              ),   
                               HGroup(Item('export_selection', editor=button_editor, show_label=False, width=0.5)),    
                        ),
                        Item('LeftPlot', editor=ComponentEditor(), show_label = False, width=590, height = 800),
                    ),
                         
                          VSplit(
                                 HGroup(
                                        VGroup(
                                               Item('Shape',                             
                                                    editor=EnumEditor(
                                                    name='Shapedropdownlist',
                                                    evaluate=validate_choice,
                                                    ),
                                               ),
                                               Item( 'shape_table', editor=TableEditor(columns_name='shape_columns',deletable = True,
                                                        sortable = False, sort_model = False, show_lines = True, line_color = "black",
                                                        editable= False, show_column_labels = False), show_label=False, width=0.3, padding=5)
                                               ),
                                        VGroup(
                                               Item('Color',                                 
                                                    editor=EnumEditor(
                                                    name='Colordropdownlist',
                                                    evaluate=validate_choice,
                                                    ),
                                               ),
                                               Item( 'color_table', editor=TableEditor(columns_name='color_columns',deletable = True,
                                                        sortable = False, sort_model = False, show_lines = True, line_color = "black",
                                                        editable= False, show_column_labels = False), show_label=False, width=0.3, padding=5)
                                               ),
                                        VGroup(
                                               Item('Size',                             
                                                    editor=EnumEditor(
                                                    name='Sizedropdownlist',
                                                    evaluate=validate_choice,
                                                    ),
                                               ),  
                                               Item( 'size_table', editor=TableEditor(columns_name='size_columns',deletable = True,
                                                        sortable = False, sort_model = False, show_lines = True, line_color = "black",
                                                        editable= False, show_column_labels = False), show_label=False, width=0.3, padding=5)
                                               ),
                               ), 
                                        
                                                                          
                               Item('RightPlot', editor=ComponentEditor(), show_label=False, height = 640),
                               
                          )

            )
             , Item( 'table',editor=table_editor, show_label=False, padding=15)      
           ),
            width=1100, height=700,
            resizable=True,
            title = "Principal Components Visualizer"
            )

    

              
    def __init__(self,PCAData, pca):
        super(PlotApp2, self).__init__()
        #self.phenotypes, self.pheno_dict = readPhenotypesFromCSVFile('..\..\IOdata\pca_phenotypes.csv')
        self.phenotypes, self.pheno_dict = readPhenotypesFromCSVFile('c:\pythondata\pca_phenotypes.csv')
        #self.phenotypes, self.pheno_dict = readPhenotypesFromCSVFile_pd('C:\Python Project\Visual_pca_6_Oct13\IOdata\phenotypes_table_2.csv')
        print(self.phenotypes, self.pheno_dict)
        self.shapes_name = self.pheno_dict[self.phenotypes[0]]
        self.colors_name = self.pheno_dict[self.phenotypes[1]]
        self.sizes_name  = self.pheno_dict[self.phenotypes[2]]
        self.colors = get_colors(len(self.colors_name))
        print('self.color=',self.colors_name)
        print('self.shape=',self.shapes_name)
        
        self.table_editor.columns =[ObjectColumn(name='name')]
        for i in range(len(PCAData)-1):
            self.table_editor.columns.append(ObjectColumn(name="PCA"+str(i)))  
        
        self.PCAData=PCAData
        self.pca=pca
        self.YPCA = [str(i) for i in range(len(PCAData)-1)]
        self.XPCA = [str(i) for i in range(len(PCAData)-1)]
        
        self.Shapedropdownlist = self.phenotypes
        self.Colordropdownlist = self.phenotypes
        self.Sizedropdownlist = self.phenotypes
        
        self.X_PCA = '0'
        self.Y_PCA = '0' 
        
        self.Shape = self.phenotypes[0]
        self.Color = self.phenotypes[1]
        self.Size = self.phenotypes[2]
        
               
        self.activeScore = 'Pre Scores'                                                                                      
        self._updateTable()
        self._updateShapeTable()
        self._updateColorTable()
        self._updateSizeTable()
        self._update_Both_graph()

        return


    def _getPCAArray(self, pcaIndex):
        x0 = []
        for batch in self.PCAData.batchs:
            if(self.active_scores_combobox == "Post Scores"):
                x0.append(batch.postscores[pcaIndex])
            else:
                x0.append(batch.prescores[pcaIndex])
        return x0  
    

 
    def _create_1D1_plot(self):
        index = 0
        plot0 = Plot(self.plotdata, padding=0)
        plot0.padding_left = 5
        plot0.padding_bottom = 5
        Container = OverlayPlotContainer(padding = 50, fill_padding = True, bgcolor = "lightgray", use_backbuffer=True)
        
        y1 =  range(len(self.PCAData.batchs[0].prescores))
        points = []
        for batch in self.PCAData.batchs:
                if (self.active_scores_combobox == "Post Scores"):
                    x1 = self.PCAData.batchs[index].postscores
                else:
                    x1 = self.PCAData.batchs[index].prescores

              
                    
                '''if (self.Shape == self.phenotypes[0]):
                    a = 1
                elif (self.Shape == self.phenotypes[1]):
                    a = batch.number
                elif (self.Shape == self.phenotypes[2]):    
                    a = batch.type
                else:
                    a = 0
                    

                if (self.Color == self.phenotypes[0]):
                    b = 0
                elif(self.Color == self.phenotypes[1]):
                    b = batch.number
                elif(self.Color == self.phenotypes[2]): 
                    b = batch.type  
                else:
                    b = 0    '''
                    
                
                a = batch.type
                b = batch.number
                
                tmarker = shapes[a]   
                bcolor = self.colors[b]
                
                                        
                for i in range(len(x1)):
                    points.append((x1[i],y1[i]))
                plot0 = create_scatter_plot((x1,y1), marker = tmarker, color=getColor(bcolor))
                
                if batch.isSelected:
                    plot0.alpha = 1
                    plot0.alpha = 1
                else:
                    plot0.fill_alpha = 0.2
                    plot0.edge_alpha = 0.2
                    
                plot0.bgcolor = "white"
                plot0.border_visible = True
                
                if index == 0:
                    value_mapper = plot0.value_mapper
                    index_mapper = plot0.index_mapper
                    add_default_grids(plot0)
                    add_default_axes(plot0, vtitle='PCA Indices', htitle='PCA Scores')
                    plot0.index_range.tight_bounds = False
                    plot0.index_range.refresh()
                    plot0.value_range.tight_bounds = False
                    plot0.value_range.refresh()
                    plot0.tools.append(PanTool(plot0))
                    zoom = ZoomTool(plot0, tool_mode="box", always_on=False,  maintain_aspect_ratio=False)
                    plot0.overlays.append(zoom)
                    dragzoom = DragZoom(plot0, drag_button="right",  maintain_aspect_ratio=False)
                    plot0.tools.append(dragzoom)
                    
                else:   
                    plot0.value_mapper = value_mapper
                    value_mapper.range.add(plot0.value)
                    plot0.index_mapper = index_mapper
                    index_mapper.range.add(plot0.index)
                if batch.isSelected:
                    Container.add(plot0)
                index = index +1

        self.RightPlot = Container                                          

   
    def _create_2D_plot(self):
        
        index = 0
        secContainer = OverlayPlotContainer(padding = 50, fill_padding = True, bgcolor = "lightgray", use_backbuffer=True)
        try:
            pcaPoints = []
            for batch in self.PCAData.batchs:
                    if (self.active_scores_combobox == "Post Scores"):
                        y = [batch.postscores[int(self.Y_PCA)]]
                        x = [batch.postscores[int(self.X_PCA)]]                        
                    else:
                        x = [batch.prescores[int(self.X_PCA)]]
                        y = [batch.prescores[int(self.Y_PCA)]]
                    for i in range(len(x)):
                        pcaPoints.append((x[i],y[i]))
                        
                        
                    ''' if (self.Shape == self.phenotypes[0]):
                        a = 1
                    elif (self.Shape == self.phenotypes[1]):
                        a = batch.number
                    elif (self.Shape == self.phenotypes[2]):    
                        a = batch.type
                    else:
                        a = 0
                        
                    if (self.Color == self.phenotypes[0]):
                        b = 0
                    elif(self.Color == self.phenotypes[1]):
                        b = batch.number
                    elif(self.Color == self.phenotypes[2]): 
                        b = batch.type  
                    else:
                        b = 0    '''
                    
                    
                    a = batch.type
                    b = batch.number
                   
                    tmarker = shapes[a]   
                    bcolor = self.colors[b]    
                                        
                    plot = create_scatter_plot((x,y), marker = tmarker, color=getColor(bcolor))
                    if batch.isSelected:
                        plot.alpha = 1
                    else:
                        plot.alpha = 0.2
                    plot.bgcolor = "white"
                    plot.border_visible = True
                    
                    
                    if index == 0:
                        value_mapper = plot.value_mapper
                        index_mapper = plot.index_mapper
                        add_default_grids(plot)
                        add_default_axes(plot, vtitle='PCA '+self.Y_PCA, htitle='PCA '+self.X_PCA)
                        plot.index_range.tight_bounds = False
                        plot.index_range.refresh()
                        plot.value_range.tight_bounds = False
                        plot.value_range.refresh()
                        
                        plot.tools.append(PanTool(plot))
                        zoom = ZoomTool(plot, tool_mode="box", always_on=False)
                        plot.overlays.append(zoom)
                        dragzoom = DragZoom(plot, drag_button="right")
                        plot.tools.append(dragzoom)
  
                    else:    
                        plot.value_mapper = value_mapper
                        value_mapper.range.add(plot.value)
                        plot.index_mapper = index_mapper
                        index_mapper.range.add(plot.index)
                    
                    if batch.isSelected:  
                        secContainer.add(plot)
                    index = index +1
            lineDraw = LineDrawer2D(plot)
            lineDraw.setPCAData(self, self.PCAData)
            plot.overlays.append(lineDraw)        
            self.LeftPlot = secContainer
        except ValueError:
        
            pass
        
              
        
    def _Y_PCA_changed(self, selectedValue):
        self.Y_PCA = selectedValue
        self._create_2D_plot()
        
    
    def _X_PCA_changed(self, selectedValue):
        self.X_PCA = selectedValue
        self._create_2D_plot()
 
    
    def _Color_changed(self, selectedValue):
        self.pcolor = selectedValue
        self.colors_name = self.pheno_dict[self.pcolor]
        self.colors = get_colors(len(self.colors_name))
        #print(self.Color, self.colors_name, self.colors)
        self._updateColorTable()
        self._update_Both_graph()
         
        
    def _Size_changed(self, selectedValue):
        self.psize = selectedValue 
        self.sizes_name = self.pheno_dict[self.psize]
        self._updateSizeTable()
        self._update_Both_graph()
        
        
    def _Shape_changed(self, selectedValue):
        self.pshape = selectedValue 
        self.shapes_name = self.pheno_dict[self.pshape]
        self._updateShapeTable()
        self._update_Both_graph() 
         
        
    def _active_scores_combobox_changed(self):
        self._update_Both_graph()        
    

    def _start_selection_fired(self):
        for batch in self.PCAData.batchs:
            batch.isSelected = False
        self._create_1D1_plot()
        self._create_2D_plot() 
        
    def _stop_selection_fired(self):
        for batch in self.PCAData.batchs:
            batch.isSelected = True
        self._create_1D1_plot()
        self._create_2D_plot()             
    
    def _export_selection_fired(self):
        path = 'c:\pythondata\out.txt'
        #path = '..\..\IOdata\out.txt'
        file1 = open(path,'w' )
        for batch in self.PCAData.batchs:
            if(batch.isSelected):
                file1.writelines(str(self.pca.pc_vars(batch.prescores))+'\n')
    
    def _updateShapeTable(self):
        del(self.shape_table)
        
        columns = [ObjectColumn(name='name')]
        for i in range(len(self.shapes_name)):
            columns.append(ObjectColumn(name='s'+self.shapes_name[i]))
        data = ShapeTable()    
        self.shape_table.append(data)        
        self.shape_columns = columns
        self.shape_table.remove(data)   
        
        data = ShapeTable()    
        data.name = self.pshape
        for i in range(len(self.shapes_name)):
            exec('data.s'+self.shapes_name[i]+'="'+self.shapes_name[i]+'"')
        self.shape_table.append(data)        
        
        data = ShapeTable()
        data.name = "Shape"
        for i in range(len(self.shapes_name)):
            exec('data.s'+self.shapes_name[i]+'="'+shapes[i]+'"')
        self.shape_table.append(data)
            
 
        
        
    def _updateColorTable(self):
        del(self.color_table)
        columns=[ObjectColumn(name='name')]
        for i in range(len(self.colors_name)):
            columns.append(ObjectColumn(name='s'+self.colors_name[i], cell_color = getColor(self.colors[i])))
        data = ColorTable()    
        self.color_table.append(data)        
        self.color_columns = columns
        self.color_table.remove(data)   
        
        data = ColorTable()
        data.name = self.pcolor
        for i in range(len(self.colors_name)):
            exec('data.s'+self.colors_name[i]+'="'+self.colors_name[i]+'"')
        self.color_table.append(data)
                
        data = ColorTable()
        data.name = "Color"
        for i in range(len(self.colors_name)):
            exec('data.s'+self.colors_name[i]+'=""')
        self.color_table.append(data)
        
            
    def _updateSizeTable(self):
        del(self.size_table)
        
        columns=[ObjectColumn(name='name')]
        for i in range(len(self.sizes_name)):
            columns.append(ObjectColumn(name='s'+self.sizes_name[i]))
        data = SizeTable()    
        self.size_table.append(data)        
        self.size_columns = columns
        self.size_table.remove(data) 
          
        data = SizeTable()    
        data.name = self.psize
        for i in range(len(self.sizes_name)):
            exec('data.s'+self.sizes_name[i]+'="'+self.sizes_name[i]+'"')
        self.size_table.append(data)        
        
        data = SizeTable()
        data.name = "Size"
        for i in range(len(self.sizes_name)):
            exec('data.s'+self.sizes_name[i]+'="'+sizes[i]+'"')
        self.size_table.append(data)
        
     
            
    
    def _updateTable(self):
        numPcaScores = len(self.PCAData)-1
        pca_vars = []
        sumVar = 0.0
        sumPercent = 0.0
        del(self.table)
            
        data = MyData()
        data.name = 'PCA Index'
        for i in range(numPcaScores):
            exec('data.PCA'+str(i)+'='+str(i))
        self.table.append(data)
        
        data = MyData()
        data.name = 'Percentage Power'
        for i in range(numPcaScores):
            pca = self._getPCAArray(i)
            temp = var(pca)
            pca_vars.append(temp)
            sumVar=sumVar+temp
        for i in range(numPcaScores):
            percent = 100*pca_vars[i]/sumVar
            exec('data.PCA'+str(i)+('=%0.2f' % percent ))
        self.table.append(data)
        
        data = MyData()
        data.name = 'Cumulative Percentage Power'
        for i in range(numPcaScores):
            percent = 100*pca_vars[i]/sumVar            
            sumPercent=sumPercent+percent
            exec('data.PCA'+str(i)+('=%0.2f' % sumPercent ))
        self.table.append(data)       
 
    def _update_Both_graph(self):
        self.activeScore = self.active_scores_combobox
        self._create_2D_plot()
        self._create_1D1_plot()
        self._updateTable() 
 


if __name__ == "__main__": 
    
    ProbsetData = makeFakeArray()
    mainData = []
    for batch in ProbsetData.batchs:        
        mainData .append( batch.score)
    
    pca = PCA_Algorithm(mainData, 47)
    
    for batch in range(len(ProbsetData.batchs)):        
       ProbsetData.batchs[batch].prescores = pca.vars_pc(ProbsetData.batchs[batch].score)
    
    f1 = PlotApp2(ProbsetData, pca)
    f1.configure_traits()
