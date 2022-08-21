import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import copy 
from skimage import io
from PIL import Image
import base64
import plotly.express as px

def create_charts():

	font_family = 'Rubik'
	chart_title_font_size = 36
	body_copy_font_size = 26
	explanation_string_font_size = body_copy_font_size
	graphic_bg_color = '#ffeee6' 
	table_line_width = 0
	# table_line_color = graphic_bg_color
	col_1_2_margin_from_top = 0.2
	col_1_2_width = 0.35
	col_3_width = 1 - (2*col_1_2_width)
	col_name_width = 0.8
	col_rating_width = 1 - col_name_width
	cell_height = 60 # this is pixels, not on 0 to 1 scale
	line_start_margin_bottom = (450 - ((4*cell_height) + (col_1_2_margin_from_top*450)))/450


	genre_ratings_csv_path = 'data/analysis/genre_wise_out_of_10.csv'
	genre_ratings_df = pd.read_csv(genre_ratings_csv_path)

	replacement_dict = {
						'amazon': 'Amazon Music',
						'apple': 'Apple Music',
						'gaana': 'Gaana',
						'hungama': 'Hungama Music',
						'jiosaavn': 'JioSaavn',
						'spotify': 'Spotify',
						'wynk': 'Wynk Music',
						'ytmusic': 'YouTube Music',
						}
	genre_ratings_df['service'].replace(replacement_dict, inplace=True)

	genres_list = genre_ratings_df.columns.values.tolist()
	#service,Rolling_Stone_500,NME_500,Blues,EDM,Hip-Hop,Jazz,Metal,Pop,R&B,Rock,Western Classical,World Music
	genres_list.remove('service')

	for genre in genres_list:
		if genre != 'Blues':continue
		genre_ratings_df_culled = genre_ratings_df[['service', genre]]
		culled_df_sorted = genre_ratings_df_culled.sort_values(by=[genre], ascending=False)

		culled_df_sorted[genre] = culled_df_sorted[genre].map('{:,.1f}'.format)

		column_dict = {	1: {'start':0, 'end': 4},
						2: {'start':4, 'end': 8},}

		fig = make_subplots(
							rows= 1, 
							cols= 3,
							horizontal_spacing=0,
							specs = [
								[
								{'type': 'table', 't': col_1_2_margin_from_top},
								{'type': 'table', 't': col_1_2_margin_from_top},
								{'type': 'image'}
								],
								],
							column_width = [col_1_2_width,
											col_1_2_width,
											col_3_width]
							)
		
		for column_number in column_dict:
			start = column_dict[column_number]['start']
			end = column_dict[column_number]['end']

			fig.add_trace(
				go.Table(
					columnwidth = [col_name_width, col_rating_width], #this is normalized to 1
					header=dict(
								values=['', ''],
								fill_color = 'black',
								# line_color = table_line_color,
								line_width = table_line_width,
								align = ['left'],
								font = dict(
										color = 'black', 
										size = body_copy_font_size,
										family = font_family,
										),
								height=0,
								),
					cells=dict(
								values=[culled_df_sorted['service'][start:end], culled_df_sorted[genre][start:end]],
								fill_color = graphic_bg_color,
								# line_color = table_line_color,
								line_width = table_line_width,
								align = ['left'],
								font = dict(
										color = 'black', 
										size = body_copy_font_size,
										family = font_family,
										),
								height= cell_height,
								),
								),
								row=1, 
								col=column_number
								)

		
		# side_image_path = "assets/smaller.png"
		side_image_path = "assets/pop_after_inkscape.png"

		img = io.imread(side_image_path)

		fig.add_trace(go.Image(
								z=img,
								x0=0,
								y0=0,
								), 
								row=1, 
								col=3
									)

		## with px.imshow 
		# fig.add_trace(px.imshow(img).data[0], 
		# 						row=1, 
		# 						col=3
		# 							)


		fig.add_shape(go.layout.Shape(
								type="line",
								yref="paper",
								xref="paper",
								x0=col_1_2_width,
								y0= line_start_margin_bottom,
								x1=col_1_2_width,
								y1= 1 - col_1_2_margin_from_top,
								line=dict(color='red', width=2),
								)
								)

		explanation_string = "XXXX"

		fig.add_annotation(
						text=explanation_string,
						font=dict(
								color="black",
								size = explanation_string_font_size,
								family = font_family,
								),
				  		xref="paper", 
						x=0,
						xanchor = 'left',
						yref="paper",
				   		y=0.08, 
						yanchor = 'middle',
				   		showarrow=False,
						align = 'left',
						)

		axis_dict = dict(
						visible=False, 
						showticklabels=False, 
						ticks="inside",
						minor_ticks="inside",
						showgrid=False,
						minor_showgrid = False,
						# ticklabelposition="inside",
						)

		fig.update_layout(
				yaxis=axis_dict,
				xaxis=axis_dict,
				# yaxis2=axis_dict,
				# xaxis2=axis_dict,
				)

		# fig.update_xaxes(visible=False, showticklabels=False, minor_ticks="",showgrid=False) # Hide x axis
		# fig.update_yaxes(visible=False, showticklabels=False, minor_ticks="",showgrid=False) # Hide y axis

		fig.update_layout(
			# autosize=False,
			height = 450, 
			width = 800,
			margin=dict(
						l=10,
						r=0,
						b=0,
						t=50,
						pad=0
					),
			title = dict(
					text = genre,
					font = dict(
							color='black', 
							size=chart_title_font_size,
							family=font_family,
							),
					x = 0.5,
					xanchor = 'center',
					xref = 'container', #the option 'paper' is for the smaller plotting area, 'container' is for the larger plot
					y = 0.97,
					yanchor = 'top',
					yref = 'container', 
					),
			paper_bgcolor=graphic_bg_color,
			)

		img_path = 'assets/' + genre + '.webp'
		fig.write_image(img_path, format='webp', scale=2)

		#crop 12 pixels from the right side
			# extra 12 px margin in plotly image
			# couldnt figure out how to get rid of it in plotly itself
		pixels_to_cut = 12
		crop_image_width = 1600 - pixels_to_cut
		base_image = Image.open(img_path)
		cropped_image = base_image.crop((0,0, crop_image_width, 900))
		cropped_image.save(img_path)


create_charts()
