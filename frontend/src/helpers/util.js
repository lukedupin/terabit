export default class Util {

    static fetch_js(url, js, succ, err) {
        let requestOptions = { method: 'GET' };
        if ( js != null ) {
            requestOptions = {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(js)
            };
        }

        //Defaults?
        if ( succ == undefined || succ == null ) {
            succ = (js) => {};
        }
        if ( err == undefined || err == null ) {
            err = (reason, code) => { console.log(reason); };
        }

        //Query
        fetch(url, requestOptions).then(resp => resp.json()).then( js => {
            if (js.successful) {
                succ(js)
            } else {
                err(js.reason, js.code)
            }
        })
    }

    static fetch_raw(url, js) {
        let requestOptions = { method: 'GET' };
        if ( js != null ) {
            requestOptions = {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(js)
            };
        }

        //Query
        return fetch(url, requestOptions).then(resp => resp.json())
    }


    //Helper to take the json blob, and break the logic paths into success and erro
    static response(js, succ, err) {
        if (js.successful) {
            succ(js)
        } else if (err != undefined) {
            err(js.reason, js.code)
        } else {
            console.error(js.reason)
        }
    }

    static xint(raw) {
        var num = parseInt(raw)
        return !isNaN(num) ? num : 0
    }

    static capitalize(string) {
        return string.charAt(0).toUpperCase() + string.slice(1)
    }

    static roundNumber(number, digits) {
        var multiple = Math.pow(10, digits);
        return Math.round(number * multiple) / multiple;
    }

    static epoch() {
        return new Date().getTime()
    }

    static epochToDate(ms) {
        var d = new Date(0)
        d.setUTCSeconds(Math.floor(ms / 1000))

        return formatDate(d)
        //return (d.getMonth() + 1) +"/"+ d.getDate() +"/"+ d.getFullYear().toString().slice(-2)
    }

    static epochToTime(ms, short) {
        var d = new Date(0)
        d.setUTCSeconds(Math.floor(ms / 1000))

        if (short === true) {
            var min = d.getMinutes()
            var hour = d.getHours()
            var am = "am"
            if (hour >= 12) {
                hour -= 12
                am = "pm"
            }

            if (hour === 0)
                hour = 12

            return hour + ":" + lpad((min % 60).toString(), 2, '0') + am
        } else
            return d.toLocaleTimeString()
    }

    static epochToDateTime(ms) {
        return epochToDate(ms) + " " + epochToTime(ms, true)
    }

    static epochExpanded(ms) {
        var date = new Date(0)
        date.setUTCSeconds(Math.floor(ms / 1000))

        //Setup the 12 hour format
        var hour = date.getHours()
        var hour_12 = hour % 12
        if (hour_12 === 0) {
            hour_12 = 12
        }

        return {
            month: date.getMonth() + 1,
            day: date.getDate(),
            year: date.getFullYear(),

            hour: hour,
            hour_12: hour_12,
            minute: date.getMinutes(),
            am_pm: (hour < 12) ? "AM" : "PM",
        }
    }

    static distanceUnits() {
        return "mi"
    }

    static elevationUnits() {
        return "ft"
    }

    static milesToMeteres(miles) {
        return miles * 1609.34
    }

    static distanceToUnits(meters, show_units) {
        //This will be updated to pull from the user's settings
        if (show_units === true)
            return (meters / 1609.34).toFixed(2) + distanceUnits()
        else
            return (meters / 1609.34).toFixed(2)
    }

    static distanceToWholeUnits(meters, show_units) {
        //This will be updated to pull from the user's settings
        if (show_units === true)
            return Math.round((meters / 1609.34)) + distanceUnits()
        else
            return Math.round((meters / 1609.34))
    }

    static elevationToUnits(meters, show_units) {
        //This will be updated to pull from the user's settings
        if (show_units === true)
            return Math.round(meters * 3.28084) + elevationUnits()
        else
            return Math.round(meters * 3.28084)
    }

    static humanDistance(meters) {
        var ft = meters * 3.28084
        if (ft > 500)
            return (ft / 5280.0).toFixed(2) + " mi"
        else if (ft > 0)
            return Math.round(ft) + " ft"
        else  //Negative? really....?
            return "0 ft"
    }

    static speedUnits() {
        return "mph"
    }

    static speedToUnits(meters_per_second, show_units) {
        var mps = meters_per_second * 2.23694
        var spd = (mps) < 100 ? mps.toFixed(1) : Math.round(mps)

        //This will be updated to pull from the user's settings
        return spd + ((show_units === true) ? speedUnits() : "")
    }

    static speedToPace(meters_per_second, show_units) {
        var mph = (meters_per_second * 2.23694)
        if (mph < 1) {
            mph = 1
        }

        var sec = 3600 / mph
        var minutes = Math.floor(sec / 60) % 60

        return minutes.toString() + ":" +
            lpad(Math.floor(sec % 60).toString(), 2, '0') +
            ((show_units === true) ? "Min/mi" : "")
    }

    static lpad(str, count, char) {
        str = str.toString()
        if (char === undefined || char === null)
            char = ' '
        while (str.length < count)
            str = char + str

        return str
    }

    static rpad(str, count, char) {
        str = str.toString()
        if (char === undefined || char === null)
            char = ' '
        while (str.length < count)
            str = str + char

        return str
    }

    static formatDate(date) {
        var year = date.getFullYear()
        var month = date.getMonth()
        var day = date.getDate()

        return (month + 1) + "/" + day + "/" + year
    }

    static formatTime(ms, show_label, am_pm) {
        var sec = Math.floor(ms / 1000)
        if (show_label === undefined || show_label === null)
            show_label = true
        if (am_pm === undefined || am_pm === null)
            am_pm = false

        //Raw data!
        if (show_label === false) {
            var min = Math.round(sec / 60)
            if (min < 60)
                return min

            return Math.floor(min / 60) + ":" + lpad((min % 60).toString(), 2, '0')
        }

        var minutes = Math.floor(sec / 60) % 60
        var hours = Math.floor(sec / 3600)

        if (!am_pm)
            return hours + ":" +
                lpad(minutes.toString(), 2, '0') + "." +
                lpad(Math.floor(sec % 60).toString(), 2, '0')


        var am = "am"
        if (hours >= 12) {
            hours -= 12
            am = "pm"
        }

        if (hours === 0)
            hours = 12
        return hours + ":" + lpad(minutes.toString(), 2, '0') + am
    }

    static formatDistance(meters) {
        var dist = Math.round(meters)
        if (dist > 1000) {
            if (dist > 100000)
                dist = Math.round(dist / 1000) // No decimial
            else
                dist = (dist / 100).toFixed(1)

            return dist + " km"
        }

        return Math.round(dist) + " m"
    }

    static simpleTimestamp(ms) {
        var sec = Math.floor((epoch() - ms) / 1000)
        if (sec < 60) {
            sec = 60
        }

        //Years
        if (sec >= 12 * 30 * 24 * 3600) {
            return Math.floor(sec / (12 * 30 * 24 * 3600)) + "yr"
        } else if (sec >= 30 * 24 * 3600) {
            return Math.floor(sec / (30 * 24 * 3600)) + "mo"
        } else if (sec >= 24 * 3600) {
            return Math.floor(sec / (24 * 3600)) + "d"
        } else if (sec >= 3600) {
            return Math.floor(sec / 3600) + "h"
        } else {
            return Math.floor(sec / 60) + "min"
        }
    }

    static durationTuple(ms) {
        if (ms < 0) {
            ms = 0
        }

        var seconds = ms / 1000

        //Pad zeros
        var min = Math.floor(seconds / 60) % 60
        var sec = Math.floor(seconds) % 60
        if (min < 10) {
            min = "0" + min
        }
        if (sec < 10) {
            sec = "0" + sec
        }

        //Write the time
        return [Math.floor(seconds / 3600) + ":" + min, sec]
    }

    static humanDuration(ms, zero_time) {
        if (zero_time === undefined || zero_time === null) {
            zero_time = "Now"
        }

        var sec = Math.floor(ms / 1000)
        if (sec <= 0)
            return zero_time
        if (sec === 1)
            return "1 second"
        if (sec < 60)
            return Math.floor(sec) + " seconds"

        var hour = Math.floor(sec / 3600)
        var min = Math.floor(sec / 60) % 60
        if (hour === 0) {
            if (min === 1)
                return "1 minute"
            else
                return min + " minutes"
        }

        if (hour === 1) {
            if (min === 0)
                return "1 hour"
            else if (min === 1)
                return "1 hour and 1 minute"
            else
                return "1 hour and " + min + " minutes"
        }

        if (min === 0)
            return hour + " hour"
        else if (min === 1)
            return hour + " hours and 1 minute"
        else
            return hour + " hours and " + min + " minutes"
    }

    static isLeapYear(date) {
        var year = date.getFullYear();
        if ((year & 3) != 0)
            return false;

        return ((year % 100) != 0 || (year % 400) == 0);
    }

// Get Day of Year
    static getDoy(date) {
        var day_count = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
        var mn = date.getMonth();
        var dn = date.getDate();
        var day_of_year = day_count[mn] + dn;
        if (mn > 1 && isLeapYear(date))
            day_of_year++;

        return day_of_year;
    }

    static isObject(obj) {
        return typeof obj === 'object' && obj !== null && Object.keys(obj).length > 0
    }

    static binaryObjSearch(ary, key, search) {
        var min = 0
        var max = ary.length - 1
        var mid

        while (min <= max) {
            mid = (min + max) >>> 1
            if (ary[mid][key] === search) {
                return mid
            } else if (ary[mid][key] < search) {
                min = mid + 1
            } else {
                max = mid - 1
            }
        }

        //Return the mid
        mid = (min + max) >>> 1
        if (mid < 0) {
            return 0
        } else if (mid >= ary.length) {
            return ary.length - 1
        } else {
            return mid
        }
    }
}