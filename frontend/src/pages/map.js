import React from 'react';

import Sidebar from "../components/sidebar";
import FilterBy from "../components/filter_by";
import Util from '../helpers/util'
import Geo from '../helpers/geo'

import mapboxgl from 'mapbox-gl/dist/mapbox-gl-unminified.js';
import MapboxWorker from 'worker-loader!mapbox-gl/dist/mapbox-gl-csp-worker';

import MapboxGeocoder from '@mapbox/mapbox-gl-geocoder';
//import '@mapbox/mapbox-gl-geocoder/dist/mapbox-gl-geocoder.css';

mapboxgl.workerClass = MapboxWorker;
mapboxgl.accessToken = 'pk.eyJ1IjoidGVyYWJpdCIsImEiOiJja21zMnpkaXMwZGdqMm5teDdpNWN1ZHVkIn0.mIPDv8iZ1mMEq51n6jt10g';

export default class Map extends React.Component {
    constructor(props) {
        super(props);

        this.updateTileSet = this.updateTileSet.bind(this);
        this.updateView = this.updateView.bind(this);
        this.handleFilter = this.handleFilter.bind(this);

        this.mapContainer = React.createRef();

        this.timerId = -1;
        this.update_view = false;
        this.new_view = false;

        this.state = {
            humans: {}
        };

        this.map_state = {
            empty: [],
            claimed: [],
            for_sale: [],
            unminted: [],

            lat: 37.7749,
            lng: -122.4194,
            zoom: 9,
            filter: {
                for_sale: true,
                claimed: true,
                empty: true,
            },
        }
    }

    componentDidMount() {
        const { lng, lat, zoom } = this.map_state;
        this.map = new mapboxgl.Map({
            container: this.mapContainer.current,
            style: 'mapbox://styles/terabit/ckn51om3s04pr17p6i2j7ojpg',
            //style: 'mapbox://styles/mapbox/streets-v11',
            center: [lng, lat],
            zoom: zoom
        });

        this.map.on('move', () => {
            this.map_state['lat'] = this.map.getCenter().lat;
            this.map_state['lng'] = this.map.getCenter().lng;
            this.map_state['zoom'] = this.map.getCenter().zoom;

            this.new_view = true;
            this.update_view = true;
        });

        let geocoder = new MapboxGeocoder({
            accessToken: mapboxgl.accessToken,
            mapboxgl: mapboxgl,
            marker: false,
        });

        this.map.addControl(geocoder, 'top-left');

        this.map.on('load', () => {
            const map = this.map;

            //Connect the result!
            geocoder.on('result', function (ev) {
                //var styleSpec = ev.result;
                //var styleSpecBox = document.getElementById('json-response');
                //var styleSpecText = JSON.stringify(styleSpec, null, 2);
                //var syntaxStyleSpecText = syntaxHighlight(styleSpecText);
                //styleSpecBox.innerHTML = syntaxStyleSpecText;
            });

            //Unminted
            map.addSource('unminted-src', {
                type: 'geojson',
                data: {
                    "type": "FeatureCollection",
                    "features": []
                },
            });
            map.addLayer({
                'id': 'unminted-poly',
                'type': 'line',
                'source': 'unminted-src',
                'layout': {},
                'paint': {
                    'line-color': '#888',
                    'line-width': 0.5,
                }
            });

            //Unclaimed info
            map.addSource('empty-src', {
                type: 'geojson',
                data: {
                    "type": "FeatureCollection",
                    "features": []
                },
            });
            map.addLayer({
                'id': 'empty-poly',
                'type': 'fill',
                'source': 'empty-src',
                'layout': {},
                'paint': {
                    'fill-color': '#26abcd',
                    'fill-opacity': 0.6,
                    'fill-outline-color': '#2cc7ef',
                }
            });

            //Claimed info
            map.addSource('claimed-src', {
                type: 'geojson',
                data: {
                    "type": "FeatureCollection",
                    "features": []
                },
            });
            map.addLayer({
                'id': 'claimed-poly',
                'type': 'fill',
                'source': 'claimed-src',
                'layout': {},
                'paint': {
                    'fill-color': '#5cd85a',
                    'fill-opacity': 0.6,
                    'fill-outline-color': '#66f064',
                }
            });

            //For sale
            map.addSource('for-sale-src', {
                type: 'geojson',
                data: {
                    "type": "FeatureCollection",
                    "features": []
                },
            });
            map.addLayer({
                'id': 'for-sale-poly',
                'type': 'fill',
                'source': 'for-sale-src',
                'layout': {},
                'paint': {
                    'fill-color': '#f2d54c',
                    'fill-opacity': 0.6,
                    'fill-outline-color': '#f0d34b',
                }
            });

            map.on('click', 'empty-poly', function (e) {
                const prop = e.features[0].properties
                map.panTo([prop.lng, prop.lat])

                new mapboxgl.Popup()
                    .setLngLat(e.lngLat)
                    .setHTML(Map.popupHtml( prop) )
                    .addTo(map);
            });
            map.on('mouseenter', 'empty-poly', function () {
                map.getCanvas().style.cursor = 'pointer';
            });
            map.on('mouseleave', 'empty-poly', function () {
                map.getCanvas().style.cursor = '';
            });

            map.on('click', 'claimed-poly', function (e) {
                const prop = e.features[0].properties
                map.panTo([prop.lng, prop.lat])

                new mapboxgl.Popup()
                    .setLngLat(e.lngLat)
                    .setHTML(Map.popupHtml( prop ) )
                    .addTo(map);
            });
            map.on('mouseenter', 'claimed-poly', function () {
                map.getCanvas().style.cursor = 'pointer';
            });
            map.on('mouseleave', 'claimed-poly', function () {
                map.getCanvas().style.cursor = '';
            });

            map.on('click', 'for-sale-poly', function (e) {
                const prop = e.features[0].properties
                map.panTo([prop.lng, prop.lat])

                new mapboxgl.Popup()
                    .setLngLat(e.lngLat)
                    .setHTML( Map.popupHtml(prop) )
                    .addTo(map);
            });
            map.on('mouseenter', 'for-sale-poly', function () {
                map.getCanvas().style.cursor = 'pointer';
            });
            map.on('mouseleave', 'for-sale-poly', function () {
                map.getCanvas().style.cursor = '';
            });

            //This has to be after the first render
            this.updateView();
            this.timerId = setInterval(this.updateViewStatefulCheck.bind(this), 150);
        });
    }

    componentWillUnmount(){
        clearInterval(this.timerId);
    }

    updateViewStatefulCheck() {
        //All of this ensure we don't double up on requests
        if (!this.update_view) {
            return
        }
        if (this.new_view) {
            this.new_view = false
            return
        }
        this.update_view = false

        //We can safely run the update view
        this.updateView();
    }

    updateView() {
        const sw = this.map.getBounds()._sw;
        const { lat, lng, zoom } = this.map_state;
        const radius = Geo.distance( lat, lng, sw.lat, sw.lng );

        //Query tiles
        Util.fetch_js('/land/search_proximity/', { lat, lng, radius }, (js) => {
            let empty = [];
            let claimed = [];
            let for_sale = [];
            let unminted = [];

            //Load up the humans
            let humans = {};
            for ( let i = 0; i < js.humans.length; i++) {
                humans[js.humans[i].uid] = js.humans[i];
            }

            //Load the lands
            for ( let i = 0; i < js.lands.length; i++) {
                const land = js.lands[i];

                const status = land.status.toLowerCase();
                const coords = Geo.boxCorners( land.lat, land.lng, 500 )

                //Setup my prop, if there is a human associated, then add them to
                let prop = {
                    ...land,
                    profile_image: '',
                    username: 'Available',
                };
                if ( land.human_uid in humans ) {
                    const human = humans[land.human_uid];

                    prop.profile_image = human.profile_image;
                    prop.username = human.username;
                    prop.nft_count += human.nft_count;
                }

                //Add the feature
                const obj = {
                    type: "Feature",
                    properties: prop,
                    geometry: {
                        type: (land.status != 'unminted')? "Polygon": "LineString",
                        coordinates: (land.status != 'unminted')? [coords]: coords,
                    }
                };

                //Add it to the correct array
                if ( status == "claimed" ) {
                    if ( land.nft_count > 0 ) {
                        claimed.push(obj);
                    }
                    else {
                        empty.push(obj);
                    }
                }
                else if ( status == "for sale" ) {
                    for_sale.push(obj);
                }
                else {
                    unminted.push(obj);
                }
            }

            //Store my data
            this.map_state.empty = empty;
            this.map_state.claimed = claimed;
            this.map_state.for_sale = for_sale;
            this.map_state.unminted = unminted;

            this.updateTileSet(this.map_state.empty, this.map_state.claimed, this.map_state.for_sale, this.map_state.unminted, this.map_state.filter );

            //Cause a state update which will update the side bar
            this.setState({ humans })
        })
    }

    updateTileSet( empty, claimed, for_sale, unminted, filter ) {
        if ( this.map.getSource('unminted-src') == undefined ) {
            return
        }

        //Update my data fields
        this.map.getSource('unminted-src').setData({
            "type": "FeatureCollection",
            "features": unminted
        })
        this.map.getSource('empty-src').setData({
            "type": "FeatureCollection",
            "features": (filter.empty)? empty: [],
        })
        this.map.getSource('claimed-src').setData({
            "type": "FeatureCollection",
            "features": (filter.claimed)? claimed: [],
        })
        this.map.getSource('for-sale-src').setData({
            "type": "FeatureCollection",
            "features": (filter.for_sale)? for_sale: [],
        })
    }

    handleFilter( filter ) {
        this.map_state.filter = filter;

        //Update!
        this.updateTileSet(
            this.map_state.empty,
            this.map_state.claimed,
            this.map_state.for_sale,
            this.map_state.unminted,
            this.map_state.filter );
    }

    handleSearch( js ) {
        map.flyTo({
            center: [ js.lng, js.lat ],
            essential: true
        });

        this.setState({
            lat: js.lat,
            lng: js.lng,
        });
    }

    static popupHtml( prop ) {
        return '<div class="user-popup-details user_activity active">' +
            '<img src="'+ prop.profile_image +'" /> ' +
            '<div>'+ prop.username +'</div>' +
            '<div>'+ prop.name +'</div>'+
            '</div>';
    }

    render() {
        //const { lng, lat, zoom } = this.map_state;
        //<Search />
        const { humans } = this.state;

        return (
            <section className="app-body">
                <div className="container-fluid">
                    <div className="row">
                        <div className="col-lg-9">
                            <div ref={this.mapContainer} className="map-grid"/>

                            <div className="map-grid-head">
                                <div className="d-flex justify-content-between">
                                    <FilterBy onChange={this.handleFilter}/>
                                </div>
                            </div>
                        </div>

                        <Sidebar humans={humans} />
                    </div>
                </div>
            </section>
    );
    }
}
