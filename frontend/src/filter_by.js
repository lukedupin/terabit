import React from 'react';

class Checkbox extends  React.Component {
    constructor(props) {
        super(props);
        console.log("Label "+ props.label)
        console.log("Tab IDX "+ props.tab_idx)
        this.state = {
            checked: true,
            label: props.label,
            tab_idx: props.tab_idx,
        };

        this.handleToggle = this.handleToggle.bind(this);
    }

    handleToggle() {
        this.setState({
            checked: !this.state.checked,
        });
    }

    render() {
        const { checked, label, tab_idx } = this.state;
        return (
            <div className="ui checkbox">
                <input
                    type="checkbox"
                    className="hidden"
                    readOnly=""
                    checked={checked}
                    onChange={this.handleToggle}
                    tabIndex={tab_idx}/>
                <label onClick={this.handleToggle}>{label}</label>
            </div>
        );
    }
}

export default class FilterBy extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            for_sale: true,
            claimed: true,
            empty: true,
        };

        this.handleChange = this.handleChange.bind(this);
    }

    componentDidMount() {
    }

    handleChange() {
        /*
        this.setState({
            search: event.target.value,
        });

        console.log("Fetch for: "+ event.target.value )
         */
    }

    render() {
        const { for_sale, claimed, empty } = this.state;
        return (
            <div className="filter_by">
                <Checkbox label="For sale" tab_idx="0" />
                <Checkbox label="Claimed" tab_idx="1" />
                <Checkbox label="Empty" tab_idx="2" />
            </div>
        );
    }
}
