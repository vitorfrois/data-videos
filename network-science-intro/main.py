from manim import *

import networkx as nx




class GraphNode:
    def __init__(self, data, position=ORIGIN, radius=0.5, neighbors=[], scale=1):
        self.char = data
        self.data = Text(str(data))
        self.data.scale(scale)
        self.neighbors = []
        self.center = position
        self.radius = radius
        self.circle = Circle(radius=radius)
        self.circle.move_to(position)
        self.data.move_to(position)
        self.drawn = False
        self.marked = False
        self.edges = []
        self.prev = None

    def connect(self, other):
        line_center = Line(self.center, other.center)
        unit_vector = line_center.get_unit_vector()
        start, end = line_center.get_start_and_end()
        new_start = start + unit_vector * self.radius
        new_end = end - unit_vector * self.radius
        line = Line(new_start, new_end)
        self.neighbors.append(other)
        other.neighbors.append(self)
        self.edges.append(line)
        other.edges.append(line)
        return line

    def connect_arrow(self, other):
        line_center = Line(self.center, other.center)
        unit_vector = line_center.get_unit_vector()
        start, end = line_center.get_start_and_end()
        new_start = start + unit_vector * self.radius / 2
        new_end = end - unit_vector * self.radius / 2
        arrow = Arrow(new_start, new_end)
        arrow.buff = self.radius / 2
        arrow.unit_vector = unit_vector
        self.neighbors.append(other)
        self.edges.append(arrow)
        return arrow

    def connect_curve(self, counter_clock_adj_self, other, clockwise_adj_other, angle=TAU / 4):
        line_self = Line(counter_clock_adj_self.circle.get_center(), self.circle.get_center())
        unit_vector_self = line_self.get_unit_vector()
        line_other = Line(clockwise_adj_other.circle.get_center(), other.circle.get_center())
        unit_vector_other = line_other.get_unit_vector()
        curve_start = self.circle.get_center() + unit_vector_self * self.radius
        curve_end = other.circle.get_center() + unit_vector_other * self.radius
        line = ArcBetweenPoints(curve_start, curve_end, angle=angle)
        self.neighbors.append(other)
        other.neighbors.append(self)
        self.edges.append(line)
        other.edges.append(line)

    def __repr__(self):
        return 'GraphNode({0})'.format(self.char)

    def __str__(self):
        return 'GraphNode({0})'.format(self.char)


class GraphScene(Scene):
    def blink_and_top(self, text, timer=3):
        self.play(Write(text))
        self.wait(2)
        self.play(text.animate().to_corner(UP))
        
    def blink(self, text, timer=2):
        rect2 = Rectangle(width=20, height=20, fill_color=BLACK, fill_opacity=1.0)
        self.play(FadeIn(rect2), run_time=0.5)
        self.play(FadeIn(text))
        self.wait(timer)
        self.play(FadeOut(text))
        self.play(FadeOut(rect2), run_time=0.5)

    def create_small_graph(self):
        graph = []
        edges = {}

        radius, scale = 0.4, 0.9
        node_0 = GraphNode('0', position=DOWN * 1 + LEFT * 3, radius=radius, scale=scale)
        node_1 = GraphNode('1', position=UP * 1 + LEFT, radius=radius, scale=scale)
        node_2 = GraphNode('2', position=DOWN * 3 + LEFT, radius=radius, scale=scale)
        node_3 = GraphNode('3', position=DOWN * 1 + RIGHT, radius=radius, scale=scale)
        # node_4 = GraphNode('4', position=DOWN * 1 + RIGHT * 3, radius=radius, scale=scale)

        # edges[(0, 1)] = node_0.connect(node_1)
        edges[(0, 2)] = node_0.connect(node_2)
        edges[(0, 3)] = node_0.connect(node_3)

        edges[(1, 3)] = node_1.connect(node_3)

        edges[(2, 3)] = node_2.connect(node_3)

        # edges[(3, 4)] = node_3.connect(node_4)

        graph.append(node_0)
        graph.append(node_1)
        graph.append(node_2)
        graph.append(node_3)
        # graph.append(node_4)

        return graph, edges

    def make_graph_mobject(self, graph, edge_dict, node_color=WHITE, stroke_color=WHITE, data_color=BLACK,
                           edge_color=GRAY_A, scale_factor=1):
        nodes = []
        edges = []
        for node in graph:
            node.circle.set_fill(color=node_color, opacity=0.5)
            node.circle.set_stroke(color=stroke_color)
            node.data.set_color(color=data_color)
            nodes.append(VGroup(node.circle, node.data))

        for edge in edge_dict.values():
            edge.set_stroke(width=7 * scale_factor)
            edge.set_color(color=edge_color)
            edges.append(edge)
        return VGroup(*nodes), VGroup(*edges)

    def sharpie_edge(self, edge_dict, u, v, color=PINK, scale_factor=1, animate=True, directed=False):
        switch = False
        if u > v:
            edge = edge_dict[(v, u)]
            switch = True
        else:
            edge = edge_dict[(u, v)]

        if not switch:
            if not directed:
                line = Line(edge.get_start(), edge.get_end())
            else:
                line = Arrow(edge.get_start() - edge.unit_vector * edge.buff,
                             edge.get_end() + edge.unit_vector * edge.buff)
        else:
            if not directed:
                line = Line(edge.get_end(), edge.get_start())
            else:
                line = Arrow(edge.get_start() - edge.unit_vector * edge.buff,
                             edge.get_end() + edge.unit_vector * edge.buff)

        if not directed:
            line.set_stroke(width=16 * scale_factor)
        else:
            line.set_stroke(width=7 * scale_factor)
        line.set_color(color)
        if animate:
            self.play(
                FadeIn(line)
            )
        return line

    def highlight_node(self, graph, index, color=BLUE_D,
                       start_angle=TAU / 2, scale_factor=1, animate=True):
        node = graph[index]
        surround_circle = Circle(radius=node.circle.radius * scale_factor)
        surround_circle.move_to(node.circle.get_center())
        # surround_circle.scale(1.15)
        surround_circle.set_stroke(width=8 * scale_factor)
        surround_circle.set_color(color)
        surround_circle.set_fill(opacity=0)
        if animate:
            self.play(
                FadeIn(surround_circle)
            )
        return surround_circle

class Thumbnail(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        pink_nabla = MathTex(r"\nabla", color='#FF90BC').scale(8).move_to(DR*0.1)
        blue_nabla = MathTex(r"\nabla", color='#6bafd6').scale(8).set_opacity(0.5).move_to(UL*0.1)
        text_input = input("Título da Thumbnail: ")
        text = Text(text_input, color=BLACK).move_to(2.5*DOWN).scale(1.5)
        self.add(pink_nabla, blue_nabla)
        self.add(text)


class LogoData(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        pink_nabla = MathTex(r"\nabla", color='#FF90BC').scale(8)
        blue_nabla = MathTex(r"\nabla", color='#6bafd6').scale(8).set_opacity(0.5)
        text = Text('data', color=WHITE).move_to(2.5*DOWN).scale(2)
        self.play(FadeIn(pink_nabla, blue_nabla))
        # self.wait()
        self.play(
            pink_nabla.animate.move_to(DR*0.1),
            blue_nabla.animate.move_to(UL*0.1),
            Write(text)
        )
        self.wait()
        self.play(FadeOut(text, pink_nabla, blue_nabla))

class DataPresentation(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        pink_nabla = MathTex(r"\nabla", color='#FF90BC').scale(8)
        blue_nabla = MathTex(r"\nabla", color='#6bafd6').scale(8).set_opacity(0.5)
        text = Text('data', color=WHITE).move_to(2.5*DOWN).scale(2)
        self.play(FadeIn(pink_nabla, blue_nabla))
        # self.wait()
        self.play(
            pink_nabla.animate.move_to(DR*0.1),
            blue_nabla.animate.move_to(UL*0.1),
            Write(text)
        )
        self.wait()
        self.play(FadeOut(text), nabla.animate.to_corner(UL))

        blist = BulletedList("Engenharia de Dados", "Ciência de Dados", "Aprendizado de Máquina", color=BLACK)

        self.play(Write(blist, run_time=6))

        self.wait()

        self.play(FadeOut(blist, nabla))

class FinalData(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        pink_nabla = MathTex(r"\nabla", color='#FF90BC').scale(8).move_to(DR*0.1)
        blue_nabla = MathTex(r"\nabla", color='#6bafd6').scale(8).set_opacity(0.5).move_to(UL*0.1)
        nabla = Group(pink_nabla, blue_nabla)
        text = Text('Obrigado por assistir!', color=BLACK).move_to(2.5*DOWN)
        # self.play(FadeIn(pink_nabla, blue_nabla))
        # self.wait()
        self.play(
            FadeIn(nabla),
            Write(text)
        )
        self.wait()
        self.play(FadeOut(text, nabla))

class Pergunta(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        text = Text('Sistemas Complexos', color=BLACK)
        self.play(Write(text))
        self.wait(1)
        self.play(FadeOut(text))


class BridgeText(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        myBaseTemplate = TexTemplate(
            documentclass="\documentclass[preview]{standalone}"
        )
        myBaseTemplate.add_to_preamble(r"\usepackage{ragged2e}")

        text = Tex(
            # "\\justifying{A Ponte Suspensa de Broughton era uma ponte suspensa de corrente de ferro construída em 1826 para atravessar o Rio Irwell entre Broughton e Pendleton, agora em Salford, Grande Manchester, Inglaterra. Uma das primeiras pontes suspensas da Europa, foi atribuída a Samuel Brown, embora alguns sugiram que tenha sido construída por Thomas Cheek Hewes, um fabricante de máquinas têxteis e mecânico de moinhos de Manchester.}",
            '\\justifying{"Comportamento complexo a partir de regras muito simples."}',
            tex_template=myBaseTemplate,
            color=BLACK
        ).scale(0.8)
        self.play(FadeIn(text))
        self.wait(5)
        self.play(FadeOut(text))


class ConceitosBasicos(GraphScene):
    def construct(self):
        self.wait()
        title = Text("Grafos")
        # title.scale(1.2)
        # title.shift(UP * 3.5)

        # self.play(
        #     Write(title)
        # )
        self.blink_and_top(title)

        self.wait()

        text_definition = Tex(
            r"Um grafo $G$ é representado por uma" + 
            "\\\\" +
            r"tupla de conjuntos $E$ e $V$."
            # r"each edge $(u, v)$ is a connection between nodes. $u, v \in V$"
        )

        math_definition = Tex(
            r"$G(E, V)$"
        )

        
        definition = VGroup(text_definition.shift(2*UP), math_definition.scale(2))

        self.play(
            Write(definition),
            run_time=5
        )

        self.wait()

        self.play(
            FadeOut(definition)
        )

        self.wait(2)

        graph, edge_dict = self.create_small_graph()
        nodes, edges = self.make_graph_mobject(graph, edge_dict)
        entire_graph = VGroup(nodes.shift(2*LEFT), edges.shift(2*LEFT))

        G_V = MathTex(
            "V=\{",
            "0", ",",
            "1", ",",
            "2", ",",
            "3", "\}"
        ).shift(UP*2 + RIGHT*3)

        list_nodes = [
            SurroundingRectangle(G_V[1], buff = .1, color=BLUE_D),
            SurroundingRectangle(G_V[3], buff = .1, color=BLUE_D),
            SurroundingRectangle(G_V[5], buff = .1, color=BLUE_D),
            SurroundingRectangle(G_V[7], buff = .1, color=BLUE_D)
        ]

        E_V = MathTex(
            "E=\{",
            "(0,2)", ",",
            "(0,3)", ",",
            "(1,3)", ",",
            "(2,3)", "\}"
        ).next_to(G_V, DOWN)


        list_edges = [
            SurroundingRectangle(E_V[1], buff = .1, color=PINK),
            SurroundingRectangle(E_V[3], buff = .1, color=PINK),
            SurroundingRectangle(E_V[5], buff = .1, color=PINK),
            SurroundingRectangle(E_V[7], buff = .1, color=PINK)
        ]


        self.play(
            Create(nodes),
            Write(G_V),
            run_time=2
        )
        self.wait(3)


        # Initialize first node
        surround_circle = self.highlight_node(graph, 0, animate=False)
        self.play(
            FadeIn(surround_circle),
            FadeIn(list_nodes[0])  
        )

        for i in range(1, len(nodes)):
            self.wait(2)
            new_surround_circle = self.highlight_node(graph, i, animate=False)
            self.play(
                ReplacementTransform(list_nodes[i-1], list_nodes[i]),
                ReplacementTransform(surround_circle, new_surround_circle) 
            )
            surround_circle = new_surround_circle

        self.play(
            FadeOut(surround_circle),
            FadeOut(list_nodes[-1])
        )


        self.play(
            Create(edges),
            Write(E_V),
            run_time=2
        )

        self.wait(3)

        # Initialize first node
        first_edge = next(iter(edge_dict))
        edge_highlight = self.sharpie_edge(edge_dict, first_edge[0], first_edge[1], animate=False)
        self.play(
            FadeIn(edge_highlight),
            FadeIn(list_edges[0])  
        )

        print(edge_dict)
        j = 0
        for i in edge_dict:
            if j != 0:
                self.wait(2)
                new_edge_highlight = self.sharpie_edge(edge_dict, i[0], i[1], animate=False)
                self.play(
                    FadeOut(edge_highlight),
                    FadeIn(new_edge_highlight), 
                    ReplacementTransform(list_edges[j-1], list_edges[j])
                )
                edge_highlight = new_edge_highlight
            j += 1

        self.wait()

        self.play(
            FadeOut(edge_highlight),
            FadeOut(G_V),
            FadeOut(E_V),
            FadeOut(list_edges[-1])
        )

        self.wait()

        node0 = self.highlight_node(graph, 0)
        node_2 = self.highlight_node(graph, 2, color=PINK, animate=False)
        node_3 = self.highlight_node(graph, 3, color=PINK, animate=False)
        k0 = MathTex("k(0) = 2").move_to(RIGHT*3 + UP)
        self.play(
            Create(node_2),
            Create(node_3),
            run_time=2
        )
        self.play(Write(k0))

        self.wait(3)



class TiposGrafos(GraphScene):
    def construct(self):
        title = Text("Tipos de Grafos")
        self.blink_and_top(title)

        self.wait(2)

        self.blink(Text("Grafos Direcionados"))
        nodes = [1, 2, 3, 4]
        edges = [(1, 2), (2, 3), (3, 4), (1, 3)]

        g = DiGraph(nodes, edges, labels=True, layout_scale=3)
        self.play(FadeIn(g))
        self.wait(10)
        self.play(FadeOut(g))

        self.blink(Text("Grafos Ponderados"))
        node_A = LabeledDot(label='1', point=2*LEFT)
        node_B = LabeledDot(label='2', point=2*RIGHT)

        # Create edges with weights
        edge_AB = Line(node_A, node_B, buff=0.1)
        weight_label = Tex("5", color=WHITE).next_to(edge_AB, UP)

        # Display nodes and edges
        self.play(Create(node_A), Create(node_B))
        self.play(Create(edge_AB), Write(weight_label))

        self.wait(10)


class MedidasBasicas(GraphScene):
    def construct(self):
        self.blink_and_top(Text("Medidas Básicas"))
        self.caminho_curto()
        self.diametro()

    def grau_medio(self):
        self.blink(Text("Grau Médio"))

        k0 = MathTex("k(0) = 2").move_to(RIGHT*3+UP*2)
        k1 = MathTex("k(1) = 1").next_to(k0, DOWN)
        k2 = MathTex("k(2) = 2").next_to(k1, DOWN)
        k3 = MathTex("k(3) = 2").next_to(k2, DOWN)

        spl_list = [k0, k1, k2, k3]

        for s in spl_list:
            self.play(Create(s))

        avg_k = MathTex("<k> = 1.75").next_to(k3, DOWN)

        self.wait(2)
        self.play(Write(avg_k))
        self.wait()

    def caminho_curto(self):
        self.blink(Text("Caminho mais curto"))

        graph, edge_dict = self.create_small_graph()
        nodes, edges = self.make_graph_mobject(graph, edge_dict)
        entire_graph = VGroup(nodes.shift(2*LEFT), edges.shift(2*LEFT))

        self.play(Create(nodes), Create(edges), run_time=3)

        self.wait(1)

        highlight1 = self.highlight_node(graph, 0, animate=False)
        highlight2 = self.highlight_node(graph, 1, animate=False)
        self.play(FadeIn(highlight1), FadeIn(highlight2))

        self.wait(3)

        edge_list = [edge for edge in edge_dict]
        first_edge = edge_list[1]
        second_edge = edge_list[2]

        self.sharpie_edge(edge_dict, first_edge[0], first_edge[1], animate=True)
        self.sharpie_edge(edge_dict, second_edge[0], second_edge[1], animate=True)
        self.wait(2)

        shortest_path_eq = MathTex("S(0,1)=\{(0,2), (2,1)\}").move_to(RIGHT*3 + UP)

        shortest_path_length = MathTex("P(0,1) = 2").next_to(shortest_path_eq, DOWN)

        self.play(Write(shortest_path_eq))
        self.play(Write(shortest_path_length))

        self.wait(2)
        self.blink(Text("Média dos caminhos mais curtos"))

        self.play(
            FadeOut(shortest_path_eq),
            FadeOut(shortest_path_length))
        
        s01 = MathTex("P(0,1) = 2").move_to(RIGHT*3+UP*2)
        s02 = MathTex("P( 0, 2) = 1").next_to(s01, DOWN)
        s03 = MathTex("P( 0, 3) = 1").next_to(s02, DOWN)
        s12 = MathTex("P( 1, 2) = 2").next_to(s03, DOWN)
        s13 = MathTex("P( 1, 3) = 1").next_to(s12, DOWN)
        s23 = MathTex("P( 2, 3) = 1").next_to(s13, DOWN)

        spl_list = [s01, s02, s03, s12, s13, s23]

        for s in spl_list:
            self.play(Create(s), run_time=0.5)

        average_spl = MathTex("<P>=1.33...").next_to(s23, DOWN*2)

        self.wait(2)
        self.play(Write(average_spl))
        self.wait(3)
        self.play(FadeOut(average_spl))

        for s in spl_list:
            self.play(FadeOut(s), run_time=0.5)

    def diametro(self): 
        self.blink(Text("Diâmetro"))
        diameter_eq = MathTex("d_G = MAX(P_G(i,j))").move_to(RIGHT*3+UP)
        diameter_result = MathTex("d_G = 2").move_to(RIGHT*3+UP)
        self.play(Write(diameter_eq))
        self.wait()
        self.play(ReplacementTransform(diameter_eq, diameter_result))

        self.wait(2)
        
class Kuramoto(GraphScene):
    purple = '#6532CD'
    def construct(self):
        vertices = [1, 2]
        edges = [(1, 2)]
        lt = {1: [-3, 0, 0], 2: [3, 0, 0]}
        g = Graph(vertices, edges, vertex_config={'radius': 0.40}, labels={1: 'J', 2: 'V'}, layout=lt)
        print(g.edges)
        for elem in [g[2], g[1], g.edges[(1,2)]]:
            self.play(Create(elem))
            self.wait()
       

        time = 10
        animation1 = self.create_animation(g[1], 5, 1)
        animation2 = self.create_animation(g[2], 5, 0.25)

        self.play(animation1, animation2)

        text = Text("'Ei, você pode piscar\num pouco mais devagar?'", font_size=24).next_to(g[1], UP)
        self.play(animation1, animation2, FadeIn(text))


        text2 = Text("'Claro!'", font_size=30).next_to(g[2], UP)
        animation1 = self.create_animation(g[1], 3, 1)
        animation2 = self.create_animation(g[2], 3, 0.5)
        self.play(animation1, animation2, Transform(text, text2))

        text3 = Text("'Você me ajudaria\npiscando mais rápido?'", font_size=30).next_to(g[2], UP)
        # animation1 = self.create_animation(g[1], 3, 1)
        # animation1 = self.create_animation(g[2], 3, 0.5)
        self.play(animation1, animation2, Transform(text, text3))

        animation1 = self.create_animation(g[1], 10, 0.5)
        animation2 = self.create_animation(g[2], 10, 0.5)
        self.play(FadeOut(text), animation1, animation2)
        

        vertices = [1, 2, 3, 4, 5, 6]
        edges = [(1, 2), (2, 3), (2, 4), (1, 5), (1, 6)]
        mg = Graph(vertices, edges, vertex_config={'radius': 0.40})
        bg = Graph.from_networkx(nx.erdos_renyi_graph(20, 0.5), layout="spring", layout_scale=3.5)

        self.play(Transform(g, mg))

        self.wait()

        self.play(Transform(g, bg))

        self.wait()


        self.play(FadeOut(g))

    def create_animation(self, dot, total_duration, blink_rate, delay: float = 0):

        dot_copy = dot.copy()
        dot_copy.color = self.purple
        num_cycles = int(total_duration // (2*blink_rate))
        animations = []
        animations.append(Wait(delay))
        for _ in range(num_cycles):
            animations.append(dot_copy.animate(run_time=0).set_opacity(1).build())
            animations.append(Wait(blink_rate))
            animations.append(dot_copy.animate(run_time=0).set_opacity(0).build())
            animations.append(Wait(blink_rate))
        return Succession(*animations, run_time=total_duration)
