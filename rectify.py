# -- IMPORTS

import bpy;
from mathutils import Vector;

# -- FUNCTIONS

def AlignEdges(
    edge_alignment_precision = 0.02,
    edge_groups_are_aligned = False
    ) :

    def IsSmallOffset( offset ) :

        return \
            offset >= -edge_alignment_precision \
            and offset <= edge_alignment_precision;

    bpy.ops.object.mode_set( mode = "OBJECT" );

    vertex_array = bpy.context.object.data.vertices;
    vertex_count = len( vertex_array );

    edge_array = bpy.context.object.data.edges;
    edge_count = len( edge_array );

    for primary_axis_index in range( 0, 3 ) :

        secondary_axis_index = ( primary_axis_index + 1 ) % 3;
        tertiary_axis_index = ( primary_axis_index + 2 ) % 3;

        for base_edge_index in range( 0, len( edge_array ) ) :

            base_edge = edge_array[ base_edge_index ];

            base_edge_offset_vector \
                = vertex_array[ base_edge.vertices[ 1 ] ].co \
                  - vertex_array[ base_edge.vertices[ 0 ] ].co;

            if IsSmallOffset( base_edge_offset_vector[ secondary_axis_index ] ) \
               and IsSmallOffset( base_edge_offset_vector[ tertiary_axis_index ] ) :

                aligned_edge_index_list = [ base_edge_index ];

                if edge_groups_are_aligned :

                    average_base_vertex \
                        = ( vertex_array[ base_edge.vertices[ 0 ] ].co \
                            + vertex_array[ base_edge.vertices[ 1 ] ].co ) * 0.5;

                    for other_edge_index in range( 0, len( edge_array ) ) :

                        if other_edge_index != base_edge_index :

                            other_edge = edge_array[ other_edge_index ];

                            edge_offset_vector \
                                = vertex_array[ other_edge.vertices[ 1 ] ].co \
                                  - vertex_array[ other_edge.vertices[ 0 ] ].co;

                            if IsSmallOffset( edge_offset_vector[ secondary_axis_index ] ) \
                               and IsSmallOffset( edge_offset_vector[ tertiary_axis_index ] ) :

                                average_other_vertex \
                                    = ( vertex_array[ other_edge.vertices[ 0 ] ].co \
                                        + vertex_array[ other_edge.vertices[ 1 ] ].co ) * 0.5;

                                edge_offset_vector = average_other_vertex - average_base_vertex;

                                if ( IsSmallOffset( edge_offset_vector[ secondary_axis_index ] )
                                     and IsSmallOffset( edge_offset_vector[ tertiary_axis_index ] ) ) :

                                    aligned_edge_index_list.append( other_edge_index );

                average_vertex = Vector( [ 0.0, 0.0, 0.0 ] );

                for aligned_edge_index in aligned_edge_index_list :

                    aligned_edge = edge_array[ aligned_edge_index ];

                    first_vertex = vertex_array[ aligned_edge.vertices[ 0 ] ];
                    second_vertex = vertex_array[ aligned_edge.vertices[ 1 ] ];

                    average_vertex += first_vertex.co;
                    average_vertex += second_vertex.co;

                average_vertex *= 0.5 / len( aligned_edge_index_list );

                for aligned_edge_index in aligned_edge_index_list :

                    aligned_edge = edge_array[ aligned_edge_index ];

                    first_vertex = vertex_array[ aligned_edge.vertices[ 0 ] ];
                    second_vertex = vertex_array[ aligned_edge.vertices[ 1 ] ];

                    first_vertex.co[ secondary_axis_index ] = average_vertex[ secondary_axis_index ];
                    second_vertex.co[ tertiary_axis_index ] = average_vertex[ tertiary_axis_index ];

# ~~

def AlignEdgeGroups(
    edge_alignment_precision = 0.02
    ) :

    AlignEdges( edge_alignment_precision, True );

# ~~

def SnapVertices(
    vertex_snapping_precision = 0.01
    ) :

    bpy.ops.object.mode_set( mode = "OBJECT" );

    vertex_array = bpy.context.object.data.vertices;

    for vertex in vertex_array:

        for axis_index in range( 0, 3 ) :

            vertex.co[ axis_index ] \
                = round( vertex.co[ axis_index ] / vertex_snapping_precision ) \
                  * vertex_snapping_precision;

# -- PROPERTIES

bpy.types.Object.edge_alignment_precision_float_property = bpy.props.FloatProperty(
    name = "Alignment Precision",
    description = "Edge Alignment Precision",
    default = 0.02,
    min = 0.001,
    max = 1.0
    );

# ~~

bpy.types.Object.edge_group_alignment_precision_float_property = bpy.props.FloatProperty(
    name = "Alignment Precision",
    description = "Edge Alignment Precision",
    default = 0.02,
    min = 0.001,
    max = 1.0
    );

# ~~

bpy.types.Object.vertex_snapping_precision_float_property = bpy.props.FloatProperty(
    name = "Snapping Precision",
    description = "Vertex Snapping Precision",
    default = 0.01,
    min = 0.001,
    max = 1.0
    );

# -- OPERATORS

class AlignEdgesOperator(
    bpy.types.Operator
    ) :

    bl_label = "Align Edges";
    bl_idname = "object.align_edges_operator";

    edge_alignment_precision_float_property : bpy.props.FloatProperty(
        name = "Alignment Precision",
        description = "Edge Alignment Precision",
        default = 0.02,
        min = 0.001,
        max = 1.0
        );

    def execute(
        self,
        context
        ) :

        AlignEdges( self.edge_alignment_precision_float_property );

        return { "FINISHED" };

# ~~

class AlignEdgeGroupsOperator(
    bpy.types.Operator
    ) :

    bl_label = "Align Edge Groups";
    bl_idname = "object.align_edge_groups_operator";

    edge_group_alignment_precision_float_property : bpy.props.FloatProperty(
        name = "Alignment Precision",
        description = "Edge Alignment Precision",
        default = 0.02,
        min = 0.001,
        max = 1.0
        );

    def execute(
        self,
        context
        ) :

        AlignEdgeGroups( self.edge_group_alignment_precision_float_property );

        return { "FINISHED" };

# ~~

class SnapVerticesOperator(
    bpy.types.Operator
    ) :

    bl_label = "Snap Vertices";
    bl_idname = "object.snap_vertices_operator";

    vertex_snapping_precision_float_property : bpy.props.FloatProperty(
        name = "Snapping Precision",
        description = "Vertex Snapping Precision",
        default = 0.01,
        min = 0.001,
        max = 1.0
        );

    def execute(
        self,
        context
        ) :

        SnapVertices( self.vertex_snapping_precision_float_property );

        return { "FINISHED" };

# -- PANELS

class RectifyMeshPanel(
    bpy.types.Panel
    ) :

    bl_idname = "OBJECT_PT_rectify_mesh";
    bl_label = "Rectify Mesh";
    bl_space_type = "PROPERTIES";
    bl_region_type = "WINDOW";
    bl_context = "object";
    bl_options = { "DEFAULT_CLOSED" };

    @classmethod
    def poll(
        class_,
        context
        ) :

        return ( context.object is not None );

    def draw(
        self,
        context
        ) :

        layout = self.layout;

        row = layout.row();
        align_edges_operator = row.operator( AlignEdgesOperator.bl_idname );
        align_edges_operator.edge_alignment_precision_float_property = context.object.edge_alignment_precision_float_property;
        row.prop( context.object, "edge_alignment_precision_float_property" );

        row = layout.row();
        align_edge_groups_operator = row.operator( AlignEdgeGroupsOperator.bl_idname );
        align_edge_groups_operator.edge_group_alignment_precision_float_property = context.object.edge_group_alignment_precision_float_property;
        row.prop( context.object, "edge_group_alignment_precision_float_property" );

        row = layout.row();
        snap_vertices_operator = row.operator( SnapVerticesOperator.bl_idname );
        snap_vertices_operator.vertex_snapping_precision_float_property = context.object.vertex_snapping_precision_float_property;
        row.prop( context.object, "vertex_snapping_precision_float_property" );

# -- STATEMENTS

bpy.utils.register_class( AlignEdgesOperator );
bpy.utils.register_class( AlignEdgeGroupsOperator );
bpy.utils.register_class( SnapVerticesOperator );
bpy.utils.register_class( RectifyMeshPanel );
