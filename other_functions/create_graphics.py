import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import copy 
from skimage import io
from PIL import Image
import base64
import plotly.express as px
from pathlib import Path

root = Path(__file__).parent.parent
font_family = 'Rubik'
chart_title_font_size = 30
title_x_y = [0.015,0.97] #xanchor left, yanchor top , also xref, yref container
subhead_string_font_size = 21
subhead_string_x_y = [0, 1] #xanchor left, yanchor top #xref, yref paper 
table_copy_font_size = 24
bottom_string_font_size = 15
bottom_string_x_y = [0, 0.045] #xanchor left, yanchor middle #xref, yref paper 
graphic_bg_color = '#ffeee6' 
table_line_width = 0
table_line_color = 'grey'
divider_x = 0.335
col_1_2_margin_from_top = 0.275
col_1_2_width = 0.35
col_3_width = 1 - (2*col_1_2_width)
col_name_width = 0.75
col_rating_width = 1 - col_name_width
cell_height = 65 # this is pixels, not on 0 to 1 scale
line_start_margin_bottom = (450 - ((4*cell_height) + (col_1_2_margin_from_top*450)))/450

# def create_genre_charts(input_csv_path):

# 	genre_ratings_df = pd.read_csv(input_csv_path)

# 	replacement_dict = {
# 						'amazon': 'Amazon Music',
# 						'apple': 'Apple Music',
# 						'gaana': 'Gaana',
# 						'hungama': 'Hungama Music',
# 						'jiosaavn': 'JioSaavn',
# 						'spotify': 'Spotify',
# 						'wynk': 'Wynk Music',
# 						'ytmusic': 'YouTube Music',
# 						}
# 	genre_ratings_df['service'].replace(replacement_dict, inplace=True)

# 	genres_list = genre_ratings_df.columns.values.tolist()
# 	#service,Rolling_Stone_500,NME_500,Blues,EDM,Hip-Hop,Jazz,Metal,Pop,R&B,Rock,Western Classical,World Music
# 	genres_list.remove('service')

# 	bottom_string_dict = {
# 						'Blues':"Flickr/Keith Ellwood",
# 						'EDM':"Flickr/emeeelea",
# 						'Hip-Hop':"Flickr/popfuzz",
# 						'Jazz':"Flickr/Kevin Tourino",
# 						'Metal':"Flickr/st3f4n",
# 						'Pop':"Flickr/Valentina Ceccatelli",
# 						'R&B':"Flickr/Patrick Gilbin",
# 						'Rock':"Flickr/Soundveil",
# 						'Western Classical':"Flickr/University of Denver",
# 						'World Music':"Flickr/San Mateo County",
# 						}

# 	for genre in genres_list:
# 		if ((genre == 'Rolling_Stone_500') or (genre == 'NME_500')): continue
# 		genre_ratings_df_culled = genre_ratings_df[['service', genre]]
# 		culled_df_sorted = genre_ratings_df_culled.sort_values(by=[genre], ascending=False)

# 		culled_df_sorted[genre] = culled_df_sorted[genre].map('{:,.1f}'.format)

# 		column_dict = {	1: {'start':0, 'end': 4},
# 						2: {'start':4, 'end': 8},}

# 		fig = make_subplots(
# 							rows= 1, 
# 							cols= 3,
# 							horizontal_spacing=0,
# 							specs = [
# 								[
# 								{'type': 'table', 't': col_1_2_margin_from_top},
# 								{'type': 'table', 't': col_1_2_margin_from_top},
# 								{'type': 'image'}
# 								],
# 								],
# 							column_width = [col_1_2_width,
# 											col_1_2_width,
# 											col_3_width]
# 							)
		
# 		for column_number in column_dict:
# 			start = column_dict[column_number]['start']
# 			end = column_dict[column_number]['end']

# 			fig.add_trace(
# 				go.Table(
# 					columnwidth = [col_name_width, col_rating_width], #this is normalized to 1
# 					header=dict(
# 								values=['', ''],
# 								fill_color = 'black',
# 								# line_color = table_line_color,
# 								line_width = table_line_width,
# 								align = ['left'],
# 								font = dict(
# 										color = 'black', 
# 										size = table_copy_font_size,
# 										family = font_family,
# 										),
# 								height=0,
# 								),
# 					cells=dict(
# 								values=[culled_df_sorted['service'][start:end], culled_df_sorted[genre][start:end]],
# 								fill_color = graphic_bg_color,
# 								line_color = table_line_color,
# 								line_width = table_line_width,
# 								align = ['left'],
# 								font = dict(
# 										color = 'black', 
# 										size = table_copy_font_size,
# 										family = font_family,
# 										),
# 								height= cell_height,
# 								),
# 								),
# 								row=1, 
# 								col=column_number
# 								)

# 		genre_fragment =\
# 			genre.lower().replace(' ', '_').replace('&', 'n').replace('-', '_')
# 		side_image_path = root / ('assets/' + genre_fragment + '_after_inkscape.png')

# 		img = io.imread(side_image_path)

# 		fig.add_trace(go.Image(
# 								z=img,
# 								x0=0,
# 								y0=0,
# 								), 
# 								row=1, 
# 								col=3
# 									)

# 		## with px.imshow 
# 		# fig.add_trace(px.imshow(img).data[0], 
# 		# 						row=1, 
# 		# 						col=3
# 		# 							)


# 		fig.add_shape(go.layout.Shape(
# 								type="line",
# 								yref="paper",
# 								xref="paper",
# 								x0=divider_x,
# 								y0= line_start_margin_bottom,
# 								x1=divider_x,
# 								y1= 1 - col_1_2_margin_from_top,
# 								line=dict(color='#ff652f', width=4),
# 								)
# 								)

# 		subhead_string = "Services in India rated out of 10. The more a service<br>" +\
# 						 "covers critically-acclaimed albums in " +\
# 						genre + ",<br>" +\
# 						 "the higher its rating."

# 		fig.add_annotation(
# 						text=subhead_string,
# 						font=dict(
# 								color="black",
# 								size = subhead_string_font_size,
# 								family = font_family,
# 								),
# 				  		xref="paper", 
# 						x= subhead_string_x_y[0],
# 						xanchor = 'left',
# 						yref="paper",
# 				   		y= subhead_string_x_y[1], 
# 						yanchor = 'top',
# 				   		showarrow=False,
# 						align = 'left',
# 						)

# 		bottom_string = 'Ratings as on Sep 4, 2022. Image: ' + bottom_string_dict[genre]

# 		fig.add_annotation(
# 						text=bottom_string,
# 						font=dict(
# 								color="black",
# 								size = bottom_string_font_size,
# 								family = font_family,
# 								),
# 				  		xref="paper", 
# 						x= bottom_string_x_y[0],
# 						xanchor = 'left',
# 						yref="paper",
# 				   		y= bottom_string_x_y[1], 
# 						yanchor = 'middle',
# 				   		showarrow=False,
# 						align = 'left',
# 						)

# 		axis_dict = dict(
# 						visible=False, 
# 						showticklabels=False, 
# 						ticks="inside",
# 						minor_ticks="inside",
# 						showgrid=False,
# 						minor_showgrid = False,
# 						# ticklabelposition="inside",
# 						)

# 		fig.update_layout(
# 				yaxis=axis_dict,
# 				xaxis=axis_dict,
# 				# yaxis2=axis_dict,
# 				# xaxis2=axis_dict,
# 				)

# 		# fig.update_xaxes(visible=False, showticklabels=False, minor_ticks="",showgrid=False) # Hide x axis
# 		# fig.update_yaxes(visible=False, showticklabels=False, minor_ticks="",showgrid=False) # Hide y axis

# 		fig.update_layout(
# 			# autosize=False,
# 			height = 450, 
# 			width = 800,
# 			margin=dict(
# 						l=10,
# 						r=0,
# 						b=0,
# 						t=50,
# 						pad=0
# 					),
# 			title = dict(
# 					text = ('<b>Best Music Service in India — ' + genre + '<b>'),
# 					font = dict(
# 							color='black', 
# 							size=chart_title_font_size,
# 							family=font_family,
# 							),
# 					x = title_x_y[0],
# 					xanchor = 'left',
# 					xref = 'container', #the option 'paper' is for the smaller plotting area, 'container' is for the larger plot
# 					y = title_x_y[1],
# 					yanchor = 'top',
# 					yref = 'container', 
# 					),
# 			paper_bgcolor=graphic_bg_color,
# 			)


# 		img_path = root / ('assets/' + genre_fragment + '_blog.webp')
# 		fig.write_image(img_path, format='webp', scale=2)

# 		#crop 12 pixels from the right side
# 			# for some reason those 12 px are blank in plotly
# 			# couldnt figure out how to get rid of it in plotly itself
# 		pixels_to_cut = 12
# 		crop_image_width = 1600 - pixels_to_cut
# 		base_image = Image.open(img_path)
# 		cropped_image = base_image.crop((0,0, crop_image_width, 900))
# 		cropped_image.save(img_path)


# input_csv_path = root / 'data/analysis/genre_wise_out_of_10.csv'

# create_genre_charts(input_csv_path)


def create_combined_genre_chart(input_csv_path):
	# make header bold 
	
	genre_ratings_df = pd.read_csv(input_csv_path)

	genre_ratings_df = genre_ratings_df[['service','Pop','EDM','Rock','Metal','Hip-Hop','R&B','Jazz','Blues','Western Classical','World Music']]

	genre_ratings_df.rename(columns = {
							'Hip-Hop':'Hip Hop',
							'Western Classical':"West'n Class'l",
							}, inplace = True)


	replacement_dict = {
						'amazon': 'Amazon',
						'apple': 'Apple',
						'gaana': 'Gaana',
						'hungama': 'Hungama',
						'jiosaavn': 'JioSaavn',
						'spotify': 'Spotify',
						'wynk': 'Wynk',
						'ytmusic': 'YouTube',
						}

	genre_ratings_df['service'].replace(replacement_dict, inplace=True)

	genres_list = genre_ratings_df.columns.values.tolist()
	genres_list.remove('service')

	service_values = genre_ratings_df['service'].values.tolist()
	header_values = ['']
	column_vectors = [service_values]

	for genre in genres_list:
		header_values.append(genre)

		genre_ratings_df[genre] = genre_ratings_df[genre].map('{:,.1f}'.format)
		genre_values = genre_ratings_df[genre].tolist()
		column_vectors.append(genre_values)

	color_map = {
				9:{'fill_color': '#1f43a9', 'font_color': '#FFFFFF'}, 
				8:{'fill_color': '#8386c6', 'font_color': '#FFFFFF'}, 
				0:{'fill_color': '#ccd0e2', 'font_color': '#000000'}
				}

	def assign_color(value):
		value = float(value)
		if value >= 9:
			return color_map[9]
		elif value >= 8:
			return color_map[8]
		else:
			return color_map[0]

	def create_matrix(typex):
		# typex here can be font_color or fill_color
		typex = typex + '_color'
		
		if typex == 'fill_color':
			colorx = 'white'
		elif typex == 'font_color':
			colorx = 'black'

		first_vector = ([colorx] * len(service_values))
		color_matrix = [first_vector]

		for vector in column_vectors[1:]:
			color_vector = []
			for val in vector:
				color = assign_color(val)[typex]
				color_vector.append(color)
			color_matrix.append(color_vector)
		
		return color_matrix

	font_color_matrix = create_matrix('font')
	fill_color_matrix = create_matrix('fill')

	fig = go.Figure()

	fig.add_trace(go.Table(
							columnwidth=([1.4] + ([1]*10)),
							header=dict(
										values=header_values,
										line_color='white',
										fill_color = 'white',
										line_width = 1,
										align = ['center'],
										font = dict(
												color = 'black', 
												size = 18,
												family = font_family,
												),
										# height = 0,		
										),
							cells=dict(
										values=column_vectors,
										line_color='white',
										line_width = 1,
										fill_color = fill_color_matrix,
										align = (['left'] +(['center']*10)),
										font_color = font_color_matrix, 
										font_size = 18,
										font_family = font_family,
										height= 30,							
										)
									)
								)
						

	fig.update_layout(
		# autosize=False,
		height = 450, 
		width = 800,
		margin=dict(
					l=10,
					r=10,
					b=10,
					t=100,
					pad=0
				),
		title = dict(
				text = ('<b>Only Spotify and Apple do well in all the genres<b>'),
				font = dict(
						color='black', 
						size= 28,
						family=font_family,
						),
				x = title_x_y[0],
				xanchor = 'left',
				xref = 'container', #the option 'paper' is for the smaller plotting area, 'container' is for the larger plot
				y = title_x_y[1],
				yanchor = 'top',
				yref = 'container', 
				),
		paper_bgcolor='white',
		)


	fig.add_annotation(
					text="Music services rated out of 10 in each genre based on availability of critically<br>acclaimed albums",
					font=dict(
							color="black",
							size = subhead_string_font_size,
							family = font_family,
							),
					xref="paper", 
					x= 0,
					xanchor = 'left',
					yref="paper",
					y= 1.16, 
					yanchor = 'top',
					showarrow=False,
					align = 'left',
					)


	fig.add_annotation(
			text= 'Source: Author analysis, data as on Sep 23, 2022',
			font=dict(
					color="black",
					size = 17,
					family = font_family,
					),
			xref="paper", 
			x= bottom_string_x_y[0],
			xanchor = 'left',
			yref="paper",
			y= bottom_string_x_y[1], 
			yanchor = 'middle',
			showarrow=False,
			align = 'left',
			)



	fig.add_shape(
		type="rect",
		x0=0.6, y0=0.025, x1=0.63, y1=0.065,
		fillcolor='#ccd0e2',
		line=dict(width=0)
	)

	fig.add_shape(
		type="rect",
		x0=0.74, y0=0.025, x1=0.77, y1=0.065,
		fillcolor='#8386c6',
		line=dict(width=0)
	)

	fig.add_shape(
		type="rect",
		x0=0.88, y0=0.025, x1=0.91, y1=0.065,
		fillcolor='#1f43a9',
		line=dict(width=0)
	)

	fig.add_annotation(
			text= '0.0-8.0',
			font=dict(
					color="black",
					size = 17,
					family = font_family,
					),
			xref="paper", 
			x= 0.635,
			xanchor = 'left',
			yref="paper",
			y= 0.04, 
			yanchor = 'middle',
			showarrow=False,
			align = 'left',
			)

	fig.add_annotation(
			text= '8.0-9.0',
			font=dict(
					color="black",
					size = 17,
					family = font_family,
					),
			xref="paper", 
			x= 0.775,
			xanchor = 'left',
			yref="paper",
			y= 0.04, 
			yanchor = 'middle',
			showarrow=False,
			align = 'left',
			)

	fig.add_annotation(
			text= '9.0-10.0',
			font=dict(
					color="black",
					size = 17,
					family = font_family,
					),
			xref="paper", 
			x= 0.915,
			xanchor = 'left',
			yref="paper",
			y= 0.04, 
			yanchor = 'middle',
			showarrow=False,
			align = 'left',
			)

	img_path = root / ('assets/combined_genre_chart.svg')
	fig.write_image(img_path, format='svg', scale=2)

input_csv_path = root / 'data/analysis/genre_wise_out_of_10.csv'

create_combined_genre_chart(input_csv_path)