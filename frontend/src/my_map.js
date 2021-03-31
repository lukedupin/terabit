import React from 'react';
import Util from './helpers/util';
import Geo from './helpers/geo';

import mapboxgl from 'mapbox-gl/dist/mapbox-gl-unminified.js';
import MapboxWorker from 'worker-loader!mapbox-gl/dist/mapbox-gl-csp-worker';

mapboxgl.workerClass = MapboxWorker;
mapboxgl.accessToken = 'pk.eyJ1IjoidGVyYWJpdCIsImEiOiJja21zMnpkaXMwZGdqMm5teDdpNWN1ZHVkIn0.mIPDv8iZ1mMEq51n6jt10g';

export default class MyMap extends React.PureComponent {
    constructor(props) {
        super(props);

        this.state = {
            lat: 37.7749,
            lng: -122.4194,
        };

        this.updateTileSet = this.updateTileSet.bind(this);
        this.updateView = this.updateView.bind(this);
        this.updateViewStatefulCheck = this.updateViewStatefulCheck.bind(this);

        this.mapContainer = React.createRef();

        this.timerId = -1;
        this.update_view = false;
        this.new_view = false;

        this.tile_data = {
            empty: [],
            claimed: [],
            for_sale: [],
            unminted: [],
        }
    }

    componentDidMount() {
        const { lng, lat } = this.state;
        this.map = new mapboxgl.Map({
            container: this.mapContainer.current,
            style: 'mapbox://styles/mapbox/streets-v11',
            center: [lng, lat],
            zoom: 9
        });

        this.map.on('move', () => {
            this.setState( {
                lng: this.map.getCenter().lng,
                lat: this.map.getCenter().lat,
            });
        });

        this.map.on('load', () => {
            const map = this.map;

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
                    'fill-color': '#Af0000',
                    'fill-opacity': 0.6,
                    'fill-outline-color': '#3F0000',
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
                    'fill-color': '#00Af00',
                    'fill-opacity': 0.6,
                    'fill-outline-color': '#003F00',
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
                    'fill-color': '#0000Af',
                    'fill-opacity': 0.6,
                    'fill-outline-color': '#00003F',
                }
            });

            map.on('click', 'empty-poly', function (e) {
                const prop = e.features[0].properties
                map.panTo([prop.lng, prop.lat])

                new mapboxgl.Popup()
                    .setLngLat(e.lngLat)
                    .setHTML(e.features[0].properties.status)
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
                    .setHTML(prop.status)
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
                    .setHTML(e.features[0].properties.status)
                    .addTo(map);
            });
            map.on('mouseenter', 'for-sale-poly', function () {
                map.getCanvas().style.cursor = 'pointer';
            });
            map.on('mouseleave', 'for-sale-poly', function () {
                map.getCanvas().style.cursor = '';
            });

            this.updateView();
            //This has to be after the first render
            this.timerId = setInterval(this.updateViewStatefulCheck.bind(this), 350);
        });
    }

    componentWillUnmount(){
        clearInterval(this.timerId);
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        this.props.onChange( this.state.lat, this.state.lng );

        //Did the props change?
        const keys = ['for_sale', 'claimed', 'empty'];
        for ( let i = 0; i < keys.length; i++ ) {
            if ( prevProps[keys[i]] != this.props[keys[i]] ) {
                this.updateTileSet( this.tile_data.empty,
                                    this.tile_data.claimed,
                                    this.tile_data.for_sale,
                                    this.tile_data.unminted,
                                    this.props.filter );
                return;
            }
        }

        //We are scrolling around and need to allow the stateful check to work
        this.new_view = true;
        this.update_view = true;
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
        //Run my view update
        const sw = this.map.getBounds()._sw;
        const { lat, lng } = this.state;

        const radius = Geo.distance( lat, lng, sw.lat, sw.lng );
        Util.fetch_js('/land/search_proximity/', { lat, lng, radius })
            .then( js => {
                Util.response(js, () => {
                    let empty = [];
                    let claimed = [];
                    let for_sale = [];
                    let unminted = [];
                    for ( let i = 0; i < js.lands.length; i++) {
                        const land = js.lands[i];

                        const status = land.status.toLowerCase();
                        const coords = Geo.boxCorners( land.lat, land.lng, 500 )

                        //Add the feature
                        const obj = {
                            type: "Feature",
                            properties: land,
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

                    //Store to stateful so we can change on the go
                    this.tile_data.empty = empty;
                    this.tile_data.claimed = claimed;
                    this.tile_data.for_sale = for_sale;
                    this.tile_data.unminted = unminted;

                    //Update the tileset
                    this.updateTileSet(
                        this.tile_data.empty,
                        this.tile_data.claimed,
                        this.tile_data.for_sale,
                        this.tile_data.unminted,
                        this.props.filter );
                })
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

    render() {
        //const { lng, lat, zoom } = this.state;
        return (
            <div ref={this.mapContainer} className="map-container" />
        );
    }
}