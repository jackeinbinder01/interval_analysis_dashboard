# Import libraries

import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output, State
import zipfile


# Import data

whole_data_set_zip = 'whole_data_set.zip'
introduction_glossary_zip = 'introduction_glossary.zip'

# Read csv from zip

def read_csv_from_zip(zip_filename, csv_filename):
    with zipfile.ZipFile(zip_filename, 'r') as zip_file:
        with zip_file.open(csv_filename) as csv_file:
            return pd.read_csv(csv_file)
        
whole_data_set = read_csv_from_zip(whole_data_set_zip, 'whole_data_set.csv')
introduction_glossary = read_csv_from_zip(introduction_glossary_zip, 'introduction_glossary.csv')

# Extract melodic & harmonic notes

whole_data_set_melodic_notes_only = whole_data_set.loc[whole_data_set['restored_indexed_note_is_melodic'] == True]
whole_data_set_harmonic_notes_only = whole_data_set.loc[whole_data_set['note_is_harmonic'] == True]

# Misc

key_center = whole_data_set['key_center']

filtered_data = whole_data_set.copy()

# Extract filter options

def get_filter_options(data):
    all_composers = data['composer'].unique()
    all_piece_composer_pairs = data['composition'].str.cat(data['composer'], sep=' - ').unique()
    all_piece_movement_pairs = data['composition'].str.cat(data['movement'], sep=' - ').unique()
    all_instruments = data['instrument_name'].unique()
    all_ensembles = data['ensemble'].unique()
    all_key_qualities = data['key_quality'].unique()

    
    return all_composers, all_piece_composer_pairs, all_piece_movement_pairs, all_ensembles, all_instruments, all_key_qualities

(all_composers, all_piece_composer_pairs, all_piece_movement_pairs, all_ensembles, all_instruments, all_key_qualities) = get_filter_options(whole_data_set)

# Card metrics

count_of_composers = whole_data_set['composer'].nunique()
count_of_pieces = whole_data_set['composition'].nunique()
count_of_movements = whole_data_set['id'].nunique()
count_of_notes = len(whole_data_set.index)
formatted_count_of_notes = '{:,}'.format(count_of_notes)

# Pie chart data

count_of_composition_composer = whole_data_set.groupby('composer')['id'].nunique()
percent_pieces_by_composer = (count_of_composition_composer / count_of_pieces) * 100

count_of_pieces_decades = whole_data_set.groupby('decade')['id'].nunique()
count_of_pieces_decades_sorted = count_of_pieces_decades.sort_index()
percent_pieces_by_decade = (count_of_pieces_decades_sorted / count_of_pieces) * 100

composition_year_min = whole_data_set['composition_year'].min()
composition_year_max = whole_data_set['composition_year'].max()
composition_year_min_string = str(composition_year_min)
composition_year_max_string = str(composition_year_max)

composition_year_range = composition_year_min_string + ' - ' + composition_year_max_string

count_of_instrument_pieces = whole_data_set.groupby('instrument_name')['id'].nunique()
percent_pieces_by_instrument = (count_of_instrument_pieces / count_of_pieces) * 100

count_of_major_minor_pieces = whole_data_set.groupby('key_quality')['id'].nunique()
percent_pieces_major_minor = (count_of_major_minor_pieces / count_of_pieces) * 100

# Diatonic v. Borrowed pie chart logic

borrowed_counts_by_movement = whole_data_set[whole_data_set['note_status'] == 'Borrowed'].groupby('id').size().reset_index(name='borrowed_count')
diatonic_counts_by_movement = whole_data_set[whole_data_set['note_status'] == 'Diatonic'].groupby('id').size().reset_index(name='diatonic_count')

total_notes_by_movement = whole_data_set.groupby('id').size().reset_index(name='count_of_notes')

borrowed_diatonic_count_by_movement = borrowed_counts_by_movement.merge(diatonic_counts_by_movement, how='left', on='id')
borrowed_v_diatonic_by_movement = borrowed_diatonic_count_by_movement.merge(total_notes_by_movement, how='left', on='id')

borrowed_v_diatonic_by_movement['Borrowed'] = borrowed_v_diatonic_by_movement['borrowed_count'] / borrowed_v_diatonic_by_movement['count_of_notes']
borrowed_v_diatonic_by_movement['Diatonic'] = borrowed_v_diatonic_by_movement['diatonic_count'] / borrowed_v_diatonic_by_movement['count_of_notes']

avg_borrowed = borrowed_v_diatonic_by_movement['Borrowed'].mean()
avg_diatonic = borrowed_v_diatonic_by_movement['Diatonic'].mean()

diatonic_v_borrowed_ratio = pd.DataFrame({'Diatonic': [avg_diatonic], 'Borrowed': [avg_borrowed]})

interval_ratios = (whole_data_set['note_interval'].value_counts() / len(whole_data_set)) * 100

# Pie chart color options

colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']

# Figure 1 - Pieces by Composer 

fig1 = go.Figure(data=[go.Pie(labels=percent_pieces_by_composer.index,
                              values=percent_pieces_by_composer.values)])
fig1.update_traces(hoverinfo='label+percent', textinfo='label', textfont_size=20,
                  marker=dict(colors=colors, line=dict(color='#000000', width=2)))

# Figure 2 - Pieces by Decade 

fig2 = go.Figure(data=[go.Pie(labels=percent_pieces_by_decade.index,
                              values=percent_pieces_by_decade.values,
                              sort=False)])

fig2.update_traces(hoverinfo='label+percent', textinfo='label', textfont_size=20,
                   marker=dict(colors=colors, line=dict(color='#000000', width=2)))

# Figure 3 - Instruments by Piece 

fig3 = go.Figure(data=[go.Pie(labels=percent_pieces_by_instrument.index,
                              values=percent_pieces_by_instrument.values)])
fig3.update_traces(hoverinfo='label+percent', textinfo='label', textfont_size=20,
                  marker=dict(colors=colors, line=dict(color='#000000', width=2)))

# Figure 4 - Major v. Minor Pieces 

fig4 = go.Figure(data=[go.Pie(labels=percent_pieces_major_minor.index,
                              values=percent_pieces_major_minor.values)])
fig4.update_traces(hoverinfo='label+percent', textinfo='label', textfont_size=20,
                  marker=dict(colors=colors, line=dict(color='#000000', width=2)))

# Figure 5 - Diatonic v. Borrowed Notes 

fig5 = go.Figure()

fig5.add_trace(go.Pie(labels=diatonic_v_borrowed_ratio.columns,
                      values=diatonic_v_borrowed_ratio.iloc[0],
                      hoverinfo='label+percent', textinfo='label', textfont_size=20,
                      marker=dict(colors=colors, line=dict(color='#000000', width=2))))
# Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}],
                suppress_callback_exceptions=True,
                )

# Dashboard page layouts

page_layouts = {

    # Introduction

    'Introduction': 
        
        dbc.Container([

            # All Pages Header

            dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H1("MusicNet Dataset - Interval Analysis Dashboard",
                                    className='card-title',
                                    style={'text-align': 'center',
                                        'margin-bottom': '10px',
                                        'display': 'inline-block',
                                        'font-size': '36px',},
                                    ),   
                                ]),
                                ], className='text-center'),   
                            ]),
                        style={'margin-top': '15px',
                            'margin-bottom': '15px',},
                        )
                    ]),
            ]),

            # Introduction Header

            dbc.Row([
                dbc.Col([
                        html.H2("Introduction", style={'text-align': 'center',
                                                        'margin-top': '15px',
                                                        'margin-bottom': '15px',}),
                        ]),
                    ]),

            # Introduction Description

            dcc.Store(id='intro-collapse-state', data={'is_open': False, 'button_text': "Read More"}),
            dbc.Row([
                dbc.Col([
                        html.P("The purpose of this analysis is to measure the ratio of specific musical intervals to all notes in a filterable sample of note level data", 
                               style={'text-align': 'left',
                                      'margin-left': '15px',
                                      'display': 'inline-block',},),                       
                        dbc.Button("Read More",
                                    id='intro-collapse-button',
                                    className='mb-3',
                                    color='light',
                                    n_clicks=0,
                                    style={'font-size': '10px',
                                           'margin': '15px',
                                           'background-color': '#CCCCCC',},),

                        # Introduction Collapse

                        dbc.Collapse(
                            html.Div([
                                html.P("This analysis is intended for musicians and composers who wish to draw quick insights, from an aggregated sample of classical pieces, based on the ratio of intervals in a sample of pieces",
                                        style={'text-align': 'left',
                                                'margin-left': '15px',
                                                'margin-right': '15px',}),
                                html.P("By understanding how often composers use certain intervals, musicians might be able to better direct their musical practice to focus on developing competencies that use more common intervallic movements rather than less common movements. For example, if in a filtered sample of pieces written in major keys, major seconds have a higher ratio than major thirds when looking at melodic notes, this may suggest that the composers in this filtered sample tend to think more in seconds than in thirds when writing melodies. This could lead one to conclude that practicing musical structures built in seconds (scales) may be more beneficial than practicing structures made in thirds (arpeggios). Additionally, if both major seconds and major thirds have high ratios compared to other major scale intervals like major sixths and major sevenths, then this could lead one to conclude that, although scale practice may supercede arpeggio practice in importance, developing competency in both scales and arpeggios may be more beneficial than developing competency in movements made out of these larger, less commonly used intervals",
                                        style={'text-align': 'left',
                                               'margin-left': '15px',}),
                            ]),
                            id='intro-collapse',
                            is_open=False,),
                        ]),
                ]),

            # Page Links

            dbc.Row([
                
                dcc.Store(id='aha-collapse-state', data={'is_open': False, 'button_text': "Read More"}),
                dcc.Store(id='isi-collapse-state', data={'is_open': False, 'button_text': "Read More"}),

                # Aggregated Harmonic Analysis Link

                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H5(html.A("Aggregated Harmonic Analysis", href='/aggregated_harmonic_analysis', style={'margin-top': '15px'}),
                                            className='card-title',
                                            id='aggregated-harmonic-analysis-link',
                                            style={'text-align': 'center',
                                                   'margin-bottom': '10px',
                                                   'display': 'inline-block',},),
                                dbc.Button("Read More",
                                           id='aha-collapse-button',
                                           className='mb-3',
                                           color='light',
                                           n_clicks=0,
                                           style={'font-size': '10px',
                                                  'background-color': '#CCCCCC',
                                                  'margin': '15px',},),
                                        ]),
                                    ], className='text-center'),

                            # Aggregated Harmonic Analysis Collapse

                            dbc.Collapse(
                                html.Div([
                                    html.P("The chart in this page displays the ratio of each musical interval (based on the parent key of a piece) to all notes in a sample of data, curated via dropdown menus. Users can filter the dataset to include only melodic (one note played at a time) vs harmonic (more than one note played at a time) passages. This page can be used to determine which intervals composers tend to use most often when writing melodies and harmonies",
                                            className='card-text')
                                    ]),
                                id='aha-collapse',
                                is_open=False,),                   
                            ]),
                        style={'margin-top': '15px',
                               'margin-bottom': '15px',},),
                    ]),
        
                # Individual Score Analysis Link
                
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                            html.H5(
                                            html.A("Individual Score Analysis", href='/individual_score_analysis', style={'margin-top': '15px'}),
                                            className='card-title',
                                            id='individual-score-analysis-link',
                                            style={'text-align': 'center',
                                                   'margin-bottom': '10px',
                                                   'display': 'inline-block',},),
                                        dbc.Button("Read More",
                                                    id='isi-collapse-button',
                                                    className='mb-3',
                                                    color='light',
                                                    n_clicks=0,
                                                    style={'font-size': '10px',
                                                            'background-color': '#CCCCCC',
                                                            'margin': '15px',},),
                                            ]),
                                        ], className='text-center'),

                                # Aggregated Harmonic Analysis Collapse

                                dbc.Collapse(
                                    html.Div([
                                        html.P("The charts in this page display the current notes, next notes, and previous notes on a particular beat in a specific movement of a specific piece. This page displays note by note information on a selected movement including note names and the instruments playing those notes. Users can move backward and forward through pieces using the next note, previous note and reset buttons. This page can be used to follow along a piece note by note, similar to reading the score but in a different view that doesn’t require one to be able to read sheet music", className='card-text'),
                                    ]),
                                id='isi-collapse',
                                is_open=False,),                            
                            ]),
                        style={'margin-top': '15px',
                               'margin-bottom': '15px',},)
                        ]),
            ]),

            # About This Dataset

            dbc.Row([
                dbc.Col([
                        html.H2("About This Dataset", 
                                style={'text-align': 'center',
                                        'margin-top': '15px',
                                        'margin-bottom': '15px',
                                        }),
                        ]),
                    ]),  

            dbc.Row([

                dcc.Store(id='atd-collapse-state', data={'is_open': False, 'button_text': "Read More"}),

                dbc.Col([
                        html.P("The information in this analysis is sourced from the MusicNet Dataset through Kaggle.com",
                                style={'text-align': 'left',
                                       'margin-left': '15px',
                                       'display': 'inline-block',},),
                        dbc.Button("Read More",
                                    id='atd-collapse-button',
                                    className='mb-3',
                                    color='light',
                                    n_clicks=0,
                                    style={'font-size': '10px',
                                            'margin': '15px',
                                            'background-color': '#CCCCCC',},),

                        # About This Dataset Collapse

                        dbc.Collapse(
                            html.Div([
                                html.P("For the purpose of this analysis, the following modifications have been made to the underlying data:",
                                        style={'text-align': 'left',
                                               'margin-left': '15px',},
                                        ),
                            html.Div([
                                html.Li("All musical data has been aggregated into a single table", style={'margin-left': '20px'}),
                                html.Li("Note values and instrument ids have been converted into pitch names (A, A#/Bb, B, etc.) and instrument names", style={'margin-left': '20px'}),
                                html.Li("A ‘Key Center’ field was added using the stated Key Center in the ‘Composition’ name field", style={'margin-left': '20px'}),
                                html.Li("i.e. If the 'Composition' is Piano Quintet in A major the 'Key Center' is A Major", style={'list-style-type': 'circle', 'text-align': 'left', 'margin-left': '60px'}),
                                html.Li("Using the new Key Center and Note Name data, musical intervals were inserted into the dataset along with a diatonic status field ‘note_status’ denoting diatonic vs borrowed notes", style={'margin-left': '20px'}),
                                html.Li("Notes have been tagged as either Harmonic or Melodic using ‘start_beat’ data", style={'margin-left': '20px'}),
                                html.Li("Notes starting on the same start beat are Harmonic because more than one note is sounding at the same time", style={'list-style-type': 'circle', 'text-align': 'left', 'margin-left': '60px',}),
                                html.Li("Notes that occur on sequential ‘start_beats’ and that sound one note at a time are Melodic because sequentially played notes that are played one note at a time must be part of standalone melodies", style={'list-style-type': 'circle', 'text-align': 'left', 'margin-left': '60px'}),
                                html.Li("A ‘Melodic Index’ has been added to rank start_beats at the granularity of the Movement",style={'margin-left': '20px'}),
                                html.Li("This enable the Current, Previous Note and Next Note charts to display note numbers relative to a movement as opposed to the beat numbers within a movement", style={'list-style-type': 'circle', 'text-align': 'left', 'margin-left': '60px'}),
                                html.Li("Composition date information for each piece was sourced and joined to the modified dataset", style={'margin-left': '20px'}),
                                ],
                                style={'text-align': 'left',
                                       'margin-left': '15px',},),

                                ]),
                            id='atd-collapse',
                            is_open=False,),                     
                ]),
            ]),

            # Glossary

            dbc.Row([
                dcc.Store(id='glossary-collapse-state', data={'is_open': False, 'button_text': "Read More"}),
                dbc.Col([
                    html.H5("Glossary", 
                            style={'text-align': 'left',
                                   'margin-top': '15px',
                                   'margin-bottom': '15px',
                                   'display': 'inline-block',}),
                    dbc.Button("Expand",
                                id='glossary-collapse-button',
                                className='mb-3',
                                color='light',
                                n_clicks=0,
                                style={'font-size': '10px',
                                        'background-color': '#CCCCCC',
                                        'margin': '15px',},),
                        ]),
                    ], className='text-left'),
            dbc.Row([
                dbc.Col([

                    # Glossary Collapse

                    dbc.Collapse(
                        html.Div([
                            dbc.Table.from_dataframe(introduction_glossary, bordered=True, hover=True, responsive=True)
                            ]),
                        id='glossary-collapse',
                        is_open=False,),
                        ]),
                    ]),
    
            # Introduction Cards

            dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            html.H4(f"{count_of_composers} Composers",
                                    className='card-title',
                                    id='count-of-composers',),
                                    ]),
                        style={'margin-bottom': '15px'},),
                        ]),
                 dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            html.H4(f"{count_of_pieces} Pieces",
                                    className='card-title',
                                    id='count-of-pieces',),
                                    ]),),
                        ]),
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            html.H4(f"{count_of_movements} Movements",
                                    className='card-title',
                                    id='count-of-movements',),
                                    ]),),
                        ]),
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            html.H4(f"{formatted_count_of_notes} Notes",
                                    className='card-title',
                                    id='count-of-notes')
                                    ]),)
                        ]),
                    ]), 

            # Introduction Pie Charts R1
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            html.H6("Pieces by Composer",
                                    className='card-subtitle',                        
                                    id='pieces-by-composer',)),
                            dbc.CardBody(dcc.Graph(figure=fig1))
                            ], body=True, style={'margin-bottom': '15px'},),
                        ]),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            html.H6(f"Pieces by Decade ({composition_year_range})",
                                    className='card-subtitle',
                                    id='pieces-by-decade',)),
                            dbc.CardBody(dcc.Graph(figure=fig2))
                            ], body=True, style={'margin-bottom': '15px'}),
                        ]),
                    ]),

            # Introduction Pie Charts R2

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            html.H6("Instruments by Piece", 
                                    className='card-subtitle',
                                    id='instruments-by-piece',)),
                            dbc.CardBody(dcc.Graph(figure=fig3))
                            ], body=True, style={'margin-bottom': '15px'},),
                        ]),
                    ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            html.H6("Major v. Minor Pieces",
                                    className='card-subtitle',
                                    id='major-v-minor')),
                            dbc.CardBody(dcc.Graph(figure=fig4))
                            ], body=True, style={'margin-bottom': '15px'}),
                        ]),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            html.H6("Diatonic v. Borrowed Notes", 
                                    className='card-subtitle',)),
                            dbc.CardBody(dcc.Graph(figure=fig5))
                            ], body=True, style={'margin-bottom': '15px'}),
                        ]),
                    ]),

            # Limitations

            dbc.Row([
                dbc.Col([
                        html.H2("Limitations", 
                                style={'text-align': 'center',
                                       'margin-bottom': '15px',}),
                        ]),
                    ]), 

            dbc.Row([
                dcc.Store(id='limitations-collapse-state', data={'is_open': False, 'button_text': "Read More"}),

                dbc.Col([
                    html.P("The modified dataset that feeds this analysis has the following limitations:",
                           style={'text-align': 'left',
                                  'margin-top': '15px',
                                  'display': 'inline-block',}),
                    dbc.Button("Read More",
                                id='limitations-collapse-button',
                                className='mb-3',
                                color='light',
                                n_clicks=0,
                                style={'font-size': '10px',
                                       'margin': '15px',
                                       'background-color': '#CCCCCC',},),

                        # Limitations Collapse

                    dbc.Collapse(
                        html.Div([
                        html.Li("Key centers are derived from the ‘composition’ field in the source data. As a result, key centers are populated at the piece level rather than at a higher level of granularity, such as the movement level", style={'margin-left': '20px'}),
                        html.Li("Outcome:", style={'list-style-type': 'circle', 'text-align': 'left', 'margin-left': '60px', 'font-weight': 'bold',}),
                        html.Li("Key changes are common in classical music, and will likely occur between movements or even within movements. When key changes occur the intervals of notes to the key center of the music will change accordingly. Because key centers are not labeled throughout the data, some intervals and diatonic v borrowed note statuses are mislabeled. As a result, the ratio of borrowed notes is overstated in this analysis", style={'list-style-type': 'square', 'text-align': 'left', 'margin-left': '90px',}),
                        html.Li("Mitigation:", style={'list-style-type': 'circle', 'text-align': 'left', 'margin-left': '60px', 'font-weight': 'bold',}),
                        html.Li("The impact of this weakness in key center data can be mitigated by identifying key changes in movements (including changes from new keys back to the original key) and labeling the key changes in the modified dataset on the ‘start_beat’ in which the key changes occur", style={'list-style-type': 'square', 'text-align': 'left', 'margin-left': '90px',}),

                        html.Li("Violin I and Violin II are not labeled as distinct entities", style={'margin-left': '20px'}),
                        html.Li("Outcome:", style={'list-style-type': 'circle', 'text-align': 'left', 'margin-left': '60px','font-weight': 'bold',}),
                        html.Li("Generally, a string quartet consists of two violins, a viola and a cello. Typically, the roles of the two violins are split into a lead role (Violin I), who plays melodies, and a supporting role (Violin II) who plays a harmonic and/or rhythmic accompaniment. Additional insights into the relationship between Violin I and Violin II could be explored if the two roles were labeled in the modified data", style={'list-style-type': 'square', 'text-align': 'left', 'margin-left': '90px',}),
                        html.Li("Mitigation:", style={'list-style-type': 'circle', 'text-align': 'left', 'margin-left': '60px','font-weight': 'bold',}),
                        html.Li("TBD", style={'list-style-type': 'square', 'text-align': 'left', 'margin-left': '90px',}),

                        html.Li("Source data provides a reference to score, but does not provide a direct link to source material", style={'margin-left': '20px'}),
                        html.Li("Outcome:", style={'list-style-type': 'circle', 'text-align': 'left', 'margin-left': '60px', 'font-weight': 'bold',}),
                        html.Li("A table that provides a link to a free-to-view sheet music source for each piece is not available for reference", style={'list-style-type': 'square', 'text-align': 'left', 'margin-left': '90px',}),
                        html.Li("Mitigation:", style={'list-style-type': 'circle', 'text-align': 'left', 'margin-left': '60px', 'font-weight': 'bold',}),
                        html.Li("Manual research into the highest quality free pdf sheet music can be performed for the 121 pieces in this dataset, which can be joined to the modified dataset and detailed in the Introduction page", style={'list-style-type': 'square', 'text-align': 'left', 'margin-left': '90px',}),

                        html.Li("Note Intervals only concern the relationship of a group of notes to the key center of a piece, rather than the interval relationship of one note to the other notes played at the same time, or the notes played next in the sequence:", style={'margin-left': '20px'}),
                        html.Li("Outcome:", style={'list-style-type': 'circle', 'text-align': 'left', 'margin-left': '60px', 'font-weight': 'bold',}),
                        html.Li("Much of the significant information in music is ignored by this analysis. Instead this analysis explores how an aggregated sample of composers might rank intervals in importance, based on their ratio to the other intervals played in a filtered selection", style={'list-style-type': 'square', 'text-align': 'left', 'margin-left': '90px',}),
                        html.Li("Mitigation:", style={'list-style-type': 'circle', 'text-align': 'left', 'margin-left': '60px', 'font-weight': 'bold',}),
                        html.Li("This analysis should not be used for the purposes of achieving a holistic understanding of a single piece or a group of pieces. A holistic understanding of a piece can only be achieved through score study & analysis and active listening", style={'list-style-type': 'square', 'text-align': 'left', 'margin-left': '90px',}),
                        html.Li("Future changes to this analysis can include MIDI windows with a Score Analyzer to enable users both read and listen to selected movements", style={'list-style-type': 'square', 'text-align': 'left', 'margin-left': '90px',}),
                        ], style={'text-align': 'left', 'margin-left': '15px', 'margin-bottom': '40px',}),
                           id='limitations-collapse',
                           is_open=False,),                    
                        ]),
            ]),
    ], fluid=True),

            
    # Aggregated Harmonic Analysis

    'aggregated_harmonic_analysis': 
    
        dbc.Container([

            # All Pages Header

            dbc.Row([
                    dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        html.H1("MusicNet Dataset - Interval Analysis Dashboard",
                                        className='card-title',
                                        style={'text-align': 'center',
                                               'display': 'inline-block',
                                               'font-size': '36px',},),
                                    ]),
                                    ], className='text-center'),   
                                ]),
                            style={'margin-top': '15px',
                                   'margin-bottom': '15px',},)
                        ]),
                ]),

            # Aggregated Harmonic Analysis Header

            dbc.Row([
                dbc.Col([
                        html.H2("Aggregated Harmonic Analysis", style={'text-align': 'center',
                                                                       'margin-top': '15px',
                                                                       'margin-bottom': '30px',}),
                        ]),
                    ]),

            # Page Links

            dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H5(
                                    html.A("Introduction", href='/', style={'margin-top': '15px'}),
                                    className='card-title',
                                    style={'text-align': 'center',
                                           'margin-bottom': '10px',
                                           'display': 'inline-block',},
                                    ),
                                ]),
                            ], className="text-center"),

                        ]),
                        style={
                            'margin-bottom': '15px',
                        },
                        ),
                    ]),
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        html.H5(
                                        html.A("Individual Score Analysis", href='/individual_score_analysis', style={'margin-top': '15px'}),
                                        className='card-title',
                                        style={'text-align': 'center',
                                               'margin-bottom': '10px',
                                               'display': 'inline-block',},),
                                    ]),
                                ], className='text-center'),   
                            ]),
                        style={'margin-bottom': '15px',},)
                    ]),
             ]),

            # Dropdown Filters

            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                                                                id='composer-dropdown',
                                                                options=[{'label': composers, 'value': composers} for composers in all_composers],
                                                                value=[],
                                                                optionHeight=30,
                                                                placeholder="Composers",
                                                                multi=True,
                                                                )
                ]),
                dbc.Col([
                    dcc.Dropdown(
                                                                id='piece-composer-dropdown',
                                                                options=[{'label': piece_composer_pairs, 'value': piece_composer_pairs} for piece_composer_pairs in all_piece_composer_pairs],
                                                                optionHeight=50,
                                                                placeholder="Pieces",
                                                                value=[],
                                                                multi=True,
                                                                )
                ]),
                dbc.Col([
                    dcc.Dropdown(
                                                                id='piece-movement-dropdown',
                                                                options=[{'label': piece_movements_pairs, 'value': piece_movements_pairs} for piece_movements_pairs in all_piece_movement_pairs],
                                                                value=[],
                                                                optionHeight=80,
                                                                placeholder="Movements",
                                                                multi=True,
                                                                )
                ]),
                dbc.Col([
                    dcc.Dropdown(
                                                                id='ensemble-dropdown',
                                                                options=[{'label': ensembles, 'value': ensembles} for ensembles in all_ensembles],
                                                                value=[],
                                                                optionHeight=30,
                                                                placeholder="Ensembles",
                                                                multi=True,
                                                                )
                ]),
                dbc.Col([
                    dcc.Dropdown(
                                                                id='instrument-dropdown',
                                                                options=[{'label': instruments, 'value': instruments} for instruments in all_instruments],
                                                                value=[],
                                                                optionHeight=30,
                                                                placeholder="Instruments",
                                                                multi=True,
                                                                )
                ]),
                dbc.Col([
                    dcc.Dropdown(
                                                                id='key-quality-dropdown',
                                                                options=[{'label': key_quality, 'value': key_quality} for key_quality in all_key_qualities],
                                                                value=[],
                                                                optionHeight=30,
                                                                placeholder="Key Quality",
                                                                multi=True,
                                                                )
                ])
                    ], style={'padding-bottom': '15px'}),

        
            # Radio Group

            dbc.Row([
                dbc.Col([
                        html.Div(
                                dbc.RadioItems(
                                    id='radio-selector',
                                    className='my-radio-items',
                                    inputClassName='btn-check',
                                    labelClassName='btn btn-outline-primary',
                                    labelCheckedClassName='active',
                                    options=[
                                            {'label': "All Notes", 'value': 1},
                                            {'label': "Harmonic Notes", 'value': 2},
                                            {'label': "Melodic Notes", 'value': 3},
                                            ],
                                    inline=True,
                                    value = 1,
                                    style={'display': 'flex',
                                           'justify-content': 'center',
                                           'width': '100%',
                                           'margin-top': '15px',}))
                    ])
            ]),
            dbc.Row([
                dbc.Col([
                        dcc.Graph(
                                    id='aha-interval-ratio-graph',
                                     figure={
                                            'data': [
                                                go.Bar(
                                                    x=interval_ratios.index,
                                                    y=interval_ratios,
                                                    texttemplate='%{y:.1f}%',
                                                    hoverinfo='none',
                                                    hovertemplate='%{x}: %{y:.1f}%',
                                                )],
                                            'layout': {
                                                'yaxis': {'title': "Ratio of intervals (against key center)", 'showticklabels': False}
                                            }
                                        },
                                    )
                        ])
                    ]),

                    ], fluid=True),

    # Individual Score Analysis

    'individual_score_analysis':
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H1("MusicNet Dataset - Interval Analysis Dashboard",
                                    className='card-title',
                                    style={'text-align': 'center',
                                           'margin-bottom': '10px',
                                           'display': 'inline-block',
                                           'font-size': '36px',},),
                                ]),
                                ], className='text-center'),   
                            ]),
                        style={'margin-top': '15px',
                               'margin-bottom': '15px',},)
                    ]),
            ]),
            dbc.Row([
                dbc.Col([
                        html.H2("Individual Score Analysis", style={'text-align': 'center',
                                                                    'margin-top': '15px',
                                                                    'margin-bottom': '30px',}),
                        ]),
                    ]),
                dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H5(
                                    html.A("Introduction", href='/', style={'margin-top': '15px'}),
                                    className='card-title',
                                    style={'text-align': 'center',
                                           'margin-bottom': '10px',
                                           'display': 'inline-block',},),
                                ]),
                            ], className='text-center'),
                        ]),
                        style={'margin-bottom': '15px',},),
                    ]),
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([

                                dbc.Row([
                                    dbc.Col([
                                        html.H5(
                                        html.A("Aggregated Harmonic Analysis", href='/aggregated_harmonic_analysis', style={'margin-top': '15px'}),
                                        className='card-title',
                                        style={'text-align': 'center',
                                               'margin-bottom': '10px',
                                               'display': 'inline-block',},
                                        ),
                                    ]),
                                ], className='text-center'),   
                            ]),
                        style={'margin-bottom': '15px',},)
                    ]),
             ]),

            # Dropdown Filters

             dbc.Row([

                dbc.Col([
                    dcc.Dropdown(
                                                                id='composer-dropdown',
                                                                options=[{'label': composers, 'value': composers} for composers in all_composers],
                                                                value=[],
                                                                optionHeight=30,
                                                                placeholder="Composers",
                                                                multi=True
                                                                )
                ]),
                dbc.Col([
                    dcc.Dropdown(
                                                                id='piece-composer-dropdown',
                                                                options=[{'label': piece_composer_pairs, 'value': piece_composer_pairs} for piece_composer_pairs in all_piece_composer_pairs],
                                                                optionHeight=50,
                                                                placeholder="Pieces",
                                                                value=[],
                                                                multi=True,
                                                                )
                ]),
                
                dbc.Col([
                    dcc.Dropdown(
                                                                id='piece-movement-dropdown',
                                                                options=[{'label': piece_movements_pairs, 'value': piece_movements_pairs} for piece_movements_pairs in all_piece_movement_pairs],
                                                                value=[],
                                                                optionHeight=80,
                                                                placeholder="Movements",
                                                                multi=True
                                                                )
                ]),

                dbc.Col([
                    dcc.Dropdown(
                                                                id='ensemble-dropdown',
                                                                options=[{'label': ensembles, 'value': ensembles} for ensembles in all_ensembles],
                                                                value=[],
                                                                optionHeight=30,
                                                                placeholder="Ensembles",
                                                                multi=True
                                                                )
                ]),
                
                dbc.Col([
                    dcc.Dropdown(
                                                                id='instrument-dropdown',
                                                                options=[{'label': instruments, 'value': instruments} for instruments in all_instruments],
                                                                value=[],
                                                                optionHeight=30,
                                                                placeholder="Instruments",
                                                                multi=True
                                                                )
                ]),


                dbc.Col([
                    dcc.Dropdown(
                                                                id='key-quality-dropdown',
                                                                options=[{'label': key_quality, 'value': key_quality} for key_quality in all_key_qualities],
                                                                value=[],
                                                                optionHeight=30,
                                                                placeholder="Key Quality",
                                                                multi=True
                                                                )
                ])
                    ], style={'padding-bottom': '15px'}),

            dbc.Row([
                    dbc.Col([
                        dbc.Card(
                                dbc.CardBody(
                                    [
                                        
                                        html.H4("", className='card-title'),
                                        html.H6(f"", className='card-title', id='individual-score-analysis-instructions',),
                                    ]
                                ),
                                style={'margin-bottom': '15px', 
                                       'text-align': 'center'},
                                ),
                        ]),
                    ]),
            dbc.Row([
                    dbc.Col([
                        dbc.Card(
                                dbc.CardBody(
                                    [
                                        
                                        html.H4("Composer", className='card-title'),
                                        html.H6(f"", className='card-title', id='individual-score-analysis-composer',),
                                    ]
                                ),
                                style={'margin-bottom': "15px", 'text-align': 'center'},
                                ),
                        ]),
                    dbc.Col([
                        dbc.Card(
                                dbc.CardBody(
                                    [
                                        
                                        html.H4("Piece", className='card-title'),
                                        html.H6(f"", className='card-title', id='individual-score-analysis-piece',),
                                    ]
                                ),
                                style={'margin-bottom': "15px", 'text-align': 'center'},
                                ),
                        ]),
                    dbc.Col([
                        dbc.Card(
                                dbc.CardBody(
                                    [
                                        
                                        html.H4("Movement", className='card-title'),
                                        html.H6(f"", className='card-title', id='individual-score-analysis-movement',),
                                    ]
                                ),
                                style={'margin-bottom': '15px', 'text-align': 'center'},
                                ),
                        ]),
                    dbc.Col([
                        dbc.Card(
                                dbc.CardBody(
                                    [
                                        
                                        html.H4("Key Center", className='card-title'),
                                        html.H6(f"", className='card-title', id='current-key-center',),
                                    ]
                                ),
                                style={'margin-bottom': '15px', 'text-align': 'center'},),
                        ]),
                    ]),

            # Previous/Next Note Buttons

            dbc.Row([
                    dbc.Col([
                            dbc.Button(
                                "Reset",
                                id='melodic-index-reset',
                                size='sm',
                                outline=False
                            ),
                            dbc.Button(
                                "< Previous Note",
                                id='melodic-index-previous-note',
                                size='sm',
                                className="w-100"
                            ),
                            dbc.Button(
                                "Next Note >",
                                id='melodic-index-next-note',
                                size='sm',
                                className="w-100"
                            ),
                        ], width=4, className='d-grid gap-2 d-md-flex justify-content-around')
                    ], className='mb-3'),

            # Current Note Graph
            dbc.Row([
                
                    dbc.Col([
                            dcc.Graph(
                            id='individual-score-analysis-current-note',
                            figure={
                                'data': [],
                                'layout': {
                                    'title': 'Current Note(s)'
                                        }
                                    })
                                ]),
                    ]),
            dbc.Row([

                    # Next Note Graph

                    dbc.Col([
                            dcc.Graph(
                            id='individual-score-analysis-next-note',
                            figure={
                                'data': [],
                                'layout': {
                                    'title': 'Next Note(s)'
                                }
                            }
                        )
                                ]),
                    # Previous Note Graph

                    dbc.Col([
                            dcc.Graph(
                            id='individial-score-analysis-previous-note',
                            figure={
                                'data': [],
                                'layout': {
                                    'title': 'Previous Note(s)'
                                }
                            }
                        )
                                ]),

                    ]),

                    # Close Container

                    ], fluid=True),
    
}



app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])



# CALLBACKS



# Page Links

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/':
        return page_layouts['Introduction']
    else:
        page_name = pathname[1:]
        if page_name in page_layouts:
            return page_layouts[page_name]
        else:
            return html.Div([
                html.H1("404 Page not found"),
                html.P(f'The requested page "{pathname}" was not found. Please navigate using the links.')
            ])
        
# Dropdowns

@app.callback( 
    [
        Output('composer-dropdown', 'options'),
        Output('piece-composer-dropdown', 'options'),
        Output('piece-movement-dropdown', 'options'),
        Output('ensemble-dropdown', 'options'),
        Output('instrument-dropdown', 'options'),
        Output('key-quality-dropdown', 'options'),
    ],
    [
        Input('composer-dropdown', 'value'),
        Input('piece-composer-dropdown', 'value'),
        Input('piece-movement-dropdown', 'value'),
        Input('ensemble-dropdown', 'value'),
        Input('instrument-dropdown', 'value'),
        Input('key-quality-dropdown', 'value'),
    ]
)
def update_dropdown_options(
    selected_composers,
    selected_piece_composer_pairs,
    selected_piece_movement_pairs,
    selected_ensembles,
    selected_instruments,
    selected_key_quality,
):

    global filtered_data
    
    filtered_data = whole_data_set.copy()

    if selected_composers:
        filtered_data = filtered_data[filtered_data['composer'].isin(selected_composers)]
    
    if selected_piece_composer_pairs:
        filtered_data = filtered_data[filtered_data['composition'].str.cat(filtered_data['composer'], sep=' - ').isin(selected_piece_composer_pairs)]

    if selected_piece_movement_pairs:
        filtered_data = filtered_data[filtered_data['composition'].str.cat(filtered_data['movement'], sep=' - ').isin(selected_piece_movement_pairs)]

    if selected_ensembles:
        filtered_data = filtered_data[filtered_data['ensemble'].isin(selected_ensembles)]

    if selected_instruments:
        filtered_data = filtered_data[filtered_data['instrument_name'].isin(selected_instruments)]

    if selected_key_quality:
        filtered_data = filtered_data[filtered_data['key_quality'].isin(selected_key_quality)]

    all_composers, all_piece_composer_pairs, all_piece_movement_pairs, all_ensembles, all_instruments, all_key_qualities = get_filter_options(filtered_data)

    return (
        [{'label': composers, 'value': composers} for composers in all_composers],
        [{'label': piece_composer_pairs, 'value': piece_composer_pairs} for piece_composer_pairs in all_piece_composer_pairs],
        [{'label': piece_movement_pairs, 'value': piece_movement_pairs} for piece_movement_pairs in all_piece_movement_pairs],
        [{'label': ensembles, 'value': ensembles} for ensembles in all_ensembles],
        [{'label': instruments, 'value': instruments} for instruments in all_instruments],
        [{'label': key_quality, 'value': key_quality} for key_quality in all_key_qualities],
    )
    


# Aggregated Harmonic Analysis - Interval Ration Graph

@app.callback(
          
    [
        Output('aha-interval-ratio-graph', 'figure'),
    ],
    [
        Input('radio-selector', 'value'),
        Input('composer-dropdown', 'value'),
        Input('piece-composer-dropdown', 'value'),
        Input('piece-movement-dropdown', 'value'),
        Input('ensemble-dropdown', 'value'),
        Input('instrument-dropdown', 'value'),
        Input('key-quality-dropdown', 'value'),

    ]
)
def update_all_notes_graph(
    radio_value,
    selected_composers,
    selected_piece_composer_pairs,
    selected_piece_movement_pairs,
    selected_ensembles,
    selected_instruments,
    selected_key_quality,
):
    filtered_data = whole_data_set.copy()

    # Apply radio filter
    if radio_value == 2:
        filtered_data = whole_data_set_harmonic_notes_only
    elif radio_value == 3:
        filtered_data = whole_data_set_melodic_notes_only

    # Apply dropdown filters
    if selected_composers:
        filtered_data = filtered_data[filtered_data['composer'].isin(selected_composers)]
    
    if selected_piece_composer_pairs:
        filtered_data = filtered_data[filtered_data['composition'].str.cat(filtered_data['composer'], sep=' - ').isin(selected_piece_composer_pairs)]

    if selected_piece_movement_pairs:
        filtered_data = filtered_data[filtered_data['composition'].str.cat(filtered_data['movement'], sep=' - ').isin(selected_piece_movement_pairs)]

    if selected_ensembles:
        filtered_data = filtered_data[filtered_data['ensemble'].isin(selected_ensembles)]

    if selected_instruments:
        filtered_data = filtered_data[filtered_data['instrument_name'].isin(selected_instruments)]

    if selected_key_quality:
        filtered_data = filtered_data[filtered_data['key_quality'].isin(selected_key_quality)]

    interval_ratios = (filtered_data['note_interval'].value_counts() / len(filtered_data)) * 100

    allnotesview = {
                'data': [
                            go.Bar(
                                x=interval_ratios.index,
                                y=interval_ratios,
                                texttemplate='%{y:.1f}%',
                                hoverinfo='none',
                                hovertemplate='%{x}: %{y:.1f}%',

                            )
                ],
                'layout': {
                    'yaxis': {'title': "Ratio of intervals (against key center)", 'showticklabels': False}   
                }
    }

    return [allnotesview]

@app.callback(
    [
        Output('individual-score-analysis-current-note', 'figure'),
        Output('individual-score-analysis-next-note', 'figure'),
        Output('individial-score-analysis-previous-note', 'figure'),
        Output('current-key-center', 'children'),
        Output('individual-score-analysis-composer','children'),
        Output('individual-score-analysis-piece', 'children'),
        Output('individual-score-analysis-movement', 'children'),
        Output('individual-score-analysis-instructions', 'children'),

    ],
    [
        Input('composer-dropdown', 'value'),
        Input('piece-composer-dropdown', 'value'),
        Input('piece-movement-dropdown', 'value'),
        Input('ensemble-dropdown', 'value'),
        Input('instrument-dropdown', 'value'),
        Input('key-quality-dropdown', 'value'),
        Input('melodic-index-reset', 'n_clicks'),
        Input('melodic-index-previous-note', 'n_clicks'),
        Input('melodic-index-next-note', 'n_clicks'),
    ],
    [
        State('individual-score-analysis-current-note', 'figure'),
        State('individual-score-analysis-next-note', 'figure'),
        State('individial-score-analysis-previous-note', 'figure'),
        State('current-key-center', 'children'),
        State('individual-score-analysis-composer','children'),
        State('individual-score-analysis-piece', 'children'),
        State('individual-score-analysis-movement', 'children'),
        State('individual-score-analysis-instructions', 'children'),
     ]
)
def update_melodic_graphs(
    selected_composers,
    selected_piece_composer_pairs,
    selected_piece_movement_pairs,
    selected_ensembles,
    selected_instruments,
    selected_key_quality,
    empty_current_note_graph,
    empty_previous_note_graph,
    empty_next_note_graph,
    current_note_graph,
    previous_note_graph,
    next_note_graph,
    current_key_center,
    individual_score_analysis_composer,
    individual_score_analysis_piece,
    individual_score_analysis_movement,
    individual_score_analysis_instructions,
):
    
    global melodic_index

    # Determine which button was clicked
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    filtered_data = whole_data_set.copy()

    empty_current_note_graph = {
        'data': [
            go.Bar(

                name="Current Note"
            )
        ],
        'layout': {
            'title': f"",
            'yaxis': {'showticklabels': False},
            'xaxis': {'showticklabels': False}
        }
    }

    empty_previous_note_graph = {
        'data': [
            go.Bar(

                name="Previous Note"
            )
        ],
        'layout': {
            'title': f"",
            'yaxis': {'showticklabels': False},
            'xaxis': {'showticklabels': False}
        }
    }

    empty_next_note_graph = {
        'data': [
            go.Bar(

                name="Next Note"
                )
            ],
            'layout': {
                'title': f"",
                'yaxis': {'showticklabels': False},
                'xaxis': {'showticklabels': False}
            }
    }
    empty_composer = ""
    empty_piece = ""
    empty_movement = ""
    empty_current_key_center = ""

    if selected_composers:
        filtered_data = filtered_data[filtered_data['composer'].isin(selected_composers)]

    if selected_piece_composer_pairs:
        filtered_data = filtered_data[filtered_data['composition'].str.cat(filtered_data['composer'], sep=' - ').isin(selected_piece_composer_pairs)]

    if selected_piece_movement_pairs:
        filtered_data = filtered_data[filtered_data['composition'].str.cat(filtered_data['movement'], sep=' - ').isin(selected_piece_movement_pairs)]
    
        if not filtered_data.empty:
            current_key_center = filtered_data['key_center'].iloc[0] + ' ' + filtered_data['key_quality'].iloc[0]
            individual_score_analysis_composer = filtered_data['composer'].iloc[0]
            individual_score_analysis_piece = filtered_data['composition'].iloc[0]
            individual_score_analysis_movement = filtered_data['movement'].iloc[0]
        else:
            current_key_center = ""
            individual_score_analysis_composer = ""
            individual_score_analysis_piece = ""
            individual_score_analysis_movement = ""

    if selected_ensembles:
        filtered_data = filtered_data[filtered_data['ensemble'].isin(selected_ensembles)]

    if selected_instruments:
        filtered_data = filtered_data[filtered_data['instrument_name'].isin(selected_instruments)]


    if selected_key_quality:
        filtered_data = filtered_data[filtered_data['key_quality'].isin(selected_key_quality)]

    empty_dropdowns = all(not var for var in (selected_composers, selected_piece_composer_pairs, selected_piece_movement_pairs, selected_ensembles, selected_instruments, selected_key_quality))

    no_buttons_clicked = all(not var for var in (triggered_id == 'melodic-index-reset', triggered_id == 'melodic-index-previous-note', triggered_id == 'melodic-index-next-note'))

   # Calculate the minimum and maximum melodic index for the filtered data
    min_melodic_index = filtered_data['melodic_index'].min()
    max_melodic_index = filtered_data['melodic_index'].max()


    # Function to find the next available melodic index
    def find_next_melodic_index(start_index, step):
        index = start_index
        while index >= min_melodic_index and index <= max_melodic_index:
            if index in filtered_data['melodic_index'].values:
                return index
            index += step

    # Update melodic index based on button clicks
    if (empty_dropdowns and no_buttons_clicked) or (selected_instruments and no_buttons_clicked):
        melodic_index = min_melodic_index
    elif triggered_id == 'melodic-index-reset':
        melodic_index = min_melodic_index
    elif triggered_id == 'melodic-index-previous-note' and melodic_index > min_melodic_index:
        melodic_index = find_next_melodic_index(melodic_index - 1, -1)
    elif triggered_id == 'melodic-index-next-note' and melodic_index < max_melodic_index:
        melodic_index = find_next_melodic_index(melodic_index + 1, 1)

    # Find the next and previous available melodic indexes
    prev_melodic_index = find_next_melodic_index(melodic_index - 1, -1)
    next_melodic_index = find_next_melodic_index(melodic_index + 1, 1)

    # Filter data for the current, next, and previous melodic indexes
    filtered_current_note = filtered_data.loc[filtered_data['melodic_index'] == melodic_index]
    filtered_prev_note = filtered_data.loc[filtered_data['melodic_index'] == prev_melodic_index]
    filtered_next_note = filtered_data.loc[filtered_data['melodic_index'] == next_melodic_index]

    grouped_current_intervals_notes = filtered_current_note.groupby(['instrument_name', 'note_interval'])['note_name'].apply(list)
    grouped_prev_intervals_notes = filtered_prev_note.groupby(['instrument_name', 'note_interval'])['note_name'].apply(list)
    grouped_next_intervals_notes = filtered_next_note.groupby(['instrument_name', 'note_interval'])['note_name'].apply(list)


    current_note_graph = {
        'data': [
            go.Bar(
                x=grouped_current_intervals_notes.index.get_level_values('note_interval'),
                y=filtered_current_note['note_interval'].value_counts().values,
                name="Current Note",
                hoverinfo='none',
                text=[
                    f"{instrument}<br><br>{', '.join(notes)}"
                    for (instrument, interval), notes in grouped_current_intervals_notes.items()
                ],
                textposition='auto',
                textfont=dict(
                    family='Arial',
                    size=12,
                )
            )
        ],
        'layout': {
            'title': f"Current Note(s) # {melodic_index}",
            'yaxis': {'showticklabels': False}
        }
    }


    if prev_melodic_index is not None:
        previous_note_graph = {
            'data': [
                go.Bar(
                    x=grouped_prev_intervals_notes.index.get_level_values('note_interval'),
                    y=filtered_prev_note['note_interval'].value_counts().values,
                    name="Current Note",
                    hoverinfo='none',
                    text=[
                        f"{instrument}<br><br>{', '.join(notes)}"
                        for (instrument, interval), notes in grouped_prev_intervals_notes.items()
                    ],
                    textposition='auto',
                    textfont=dict(
                        family='Arial',
                        size=12,
                    )
                )
            ],
            'layout': {
                'title': f"Previous Note(s) # {prev_melodic_index}" if prev_melodic_index is not None else f"Previous Note(s) # ",
                'yaxis': {'showticklabels': False}
            }
        }
    
    else:
        previous_note_graph = {
        'data': [
            go.Bar(

                name="Previous Note"
            )
        ],
        'layout': {
            'title': f"Previous Note(s) # ",
            'yaxis': {'showticklabels': False},
            'xaxis': {'showticklabels': False}
        }
    }


    next_note_graph = {
        'data': [
            go.Bar(
                x=grouped_next_intervals_notes.index.get_level_values('note_interval'),
                y=filtered_next_note['note_interval'].value_counts().values,
                name="Next Note",
                hoverinfo='none',
                text=[
                    f"{instrument}<br><br>{', '.join(notes)}"
                    for (instrument, interval), notes in grouped_next_intervals_notes.items()
                ],
                textposition='auto',
                textfont=dict(
                    family='Arial',
                    size=12,
                )
            )
        ],

        'layout': {
            'title': f"Next Note(s) # {next_melodic_index}",
            'yaxis': {'showticklabels': False}
        }
    }

    individual_score_analysis_instructions = ""
     

    if not selected_piece_movement_pairs:
        return (
                empty_current_note_graph,
                empty_previous_note_graph,
                empty_next_note_graph,
                empty_composer,
                empty_piece,
                empty_movement,
                empty_current_key_center,
                html.H4("Select a piece and movement to begin", className='card-title'),
            )
    else:

        return current_note_graph, previous_note_graph, next_note_graph, current_key_center, individual_score_analysis_composer, individual_score_analysis_piece, individual_score_analysis_movement, individual_score_analysis_instructions

    


@app.callback(
    Output('intro-collapse', 'is_open'),
    [Input('intro-collapse-button', 'n_clicks')],
    [State('intro-collapse', 'is_open')],
)
def toggle_intro_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output('aha-collapse', 'is_open'),
    [Input('aha-collapse-button', 'n_clicks')],
    [State('aha-collapse', 'is_open')],
)
def toggle_aha_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output('isi-collapse', 'is_open'),
    [Input('isi-collapse-button', 'n_clicks')],
    [State('isi-collapse', 'is_open')],
)
def toggle_isi_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    [
        Output('intro-collapse-button', 'children'),
        Output('intro-collapse-state', 'data'),
    ],
    [
        Input('intro-collapse', 'is_open'),
        Input('intro-collapse-state', 'data'),
    ],
)
def toggle_button_text_intro(is_open, data):
    if is_open:
        button_text = "Read Less"
    else:
        button_text = "Read More"
    
    data['is_open'] = not is_open
    data['button_text'] = button_text

    return button_text, data
@app.callback(
    [
        Output('aha-collapse-button', 'children'),
        Output('aha-collapse-state', 'data'),
    ],
    [
        Input('aha-collapse', 'is_open'),
        Input('aha-collapse-state', 'data'),
    ],
)
def toggle_button_text_aha(is_open, data):
    if is_open:
        button_text = "Read Less"
    else:
        button_text = "Read More"
    
    data['is_open'] = not is_open
    data['button_text'] = button_text

    return button_text, data

@app.callback(
    [
        Output('isi-collapse-button', 'children'),
        Output('isi-collapse-state', 'data'),
    ],
    [
        Input('isi-collapse', 'is_open'),
        Input('isi-collapse-state', 'data'),
    ],
)
def toggle_button_text_isi(is_open, data):
    if is_open:
        button_text = "Read Less"
    else:
        button_text = "Read More"
    
    data['is_open'] = not is_open
    data['button_text'] = button_text

    return button_text, data

@app.callback(
    Output('glossary-collapse', 'is_open'),
    [Input('glossary-collapse-button', 'n_clicks')],
    [State('glossary-collapse', 'is_open')],
)
def toggle_glossary_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    [
        Output('glossary-collapse-button', 'children'),
        Output('glossary-collapse-state', 'data'),
    ],
    [
        Input('glossary-collapse', 'is_open'),
        Input('glossary-collapse-state', 'data'),
    ],
)
def toggle_button_text_glossary(is_open, data):
    if is_open:
        button_text = "Contract"
    else:
        button_text = "Expand"
    
    data['is_open'] = not is_open
    data['button_text'] = button_text

    return button_text, data

@app.callback(
    [
        Output('atd-collapse-button', 'children'),
        Output('atd-collapse-state', 'data'),
    ],
    [
        Input('atd-collapse', 'is_open'),
        Input('atd-collapse-state', 'data'),
    ],
)
def toggle_button_text_atd(is_open, data):
    if is_open:
        button_text = "Read Less"
    else:
        button_text = "Read More"
    
    data['is_open'] = not is_open
    data['button_text'] = button_text

    return button_text, data

@app.callback(
    Output('atd-collapse', 'is_open'),
    [Input('atd-collapse-button', 'n_clicks')],
    [State('atd-collapse', 'is_open')],
)
def toggle_atd_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    [
        Output('limitations-collapse-button', 'children'),
        Output('limitations-collapse-state', 'data'),
    ],
    [
        Input('limitations-collapse', 'is_open'),
        Input('limitations-collapse-state', 'data'),
    ],
)
def toggle_button_text_limitations(is_open, data):
    if is_open:
        button_text = "Read Less"
    else:
        button_text = "Read More"
    
    data['is_open'] = not is_open
    data['button_text'] = button_text

    return button_text, data

@app.callback(
    Output('limitations-collapse', 'is_open'),
    [Input('limitations-collapse-button', 'n_clicks')],
    [State('limitations-collapse', 'is_open')],
)
def toggle_limitations_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run_server(debug=True)