// LyricPeakMapper.jsx
// Creates lyric markers and text keyframes based on pasted lyrics and an audio amplitude layer.
// Requires the user to run "Convert Audio to Keyframes" on the audio layer first.

(function lyricPeakMapper(thisObj) {
    function buildUI(thisObj) {
        var palette = (thisObj instanceof Panel) ? thisObj : new Window("palette", "Lyric Peak Mapper", undefined, {resizeable: true});
        if (!palette) {
            return palette;
        }

        palette.alignChildren = "fill";

        var compGroup = palette.add("group");
        compGroup.orientation = "column";
        compGroup.alignChildren = "fill";
        compGroup.add("statictext", undefined, "Active Comp: " + (app.project && app.project.activeItem ? app.project.activeItem.name : "None"));

        var audioGroup = palette.add("group");
        audioGroup.orientation = "row";
        audioGroup.add("statictext", undefined, "Amplitude Layer:");
        var audioDropdown = audioGroup.add("dropdownlist", undefined);
        audioDropdown.minimumSize.width = 220;

        var thresholdGroup = palette.add("group");
        thresholdGroup.orientation = "row";
        thresholdGroup.add("statictext", undefined, "Peak Threshold:");
        var thresholdInput = thresholdGroup.add("edittext", undefined, "10");
        thresholdInput.characters = 6;

        var spacingGroup = palette.add("group");
        spacingGroup.orientation = "row";
        spacingGroup.add("statictext", undefined, "Min Spacing (sec):");
        var spacingInput = spacingGroup.add("edittext", undefined, "0.25");
        spacingInput.characters = 6;

        var lyricsGroup = palette.add("group");
        lyricsGroup.orientation = "column";
        lyricsGroup.alignChildren = "fill";
        lyricsGroup.add("statictext", undefined, "Paste lyrics (words or lines):");
        var lyricsBox = lyricsGroup.add("edittext", undefined, "", {multiline: true, wantReturn: true});
        lyricsBox.preferredSize = [320, 160];

        var buttons = palette.add("group");
        buttons.alignment = "right";
        var runButton = buttons.add("button", undefined, "Create Markers");

        populateAudioDropdown(audioDropdown);

        runButton.onClick = function () {
            app.beginUndoGroup("Lyric Peak Mapper");
            try {
                var activeComp = app.project && app.project.activeItem && (app.project.activeItem instanceof CompItem) ? app.project.activeItem : null;
                if (!activeComp) {
                    alert("Please select an active composition first.");
                    return;
                }

                var layer = audioDropdown.selection ? audioDropdown.selection.layerRef : null;
                if (!layer) {
                    alert("Choose an audio amplitude layer (generated from Convert Audio to Keyframes).");
                    return;
                }

                var slider = findAudioAmplitudeSlider(layer);
                if (!slider) {
                    alert("The selected layer is missing the 'Audio Amplitude' slider. Run Convert Audio to Keyframes first.");
                    return;
                }

                var threshold = parseFloat(thresholdInput.text);
                if (isNaN(threshold)) {
                    threshold = 10;
                }

                var spacing = parseFloat(spacingInput.text);
                if (isNaN(spacing) || spacing <= 0) {
                    spacing = 0.25;
                }

                var lyrics = lyricsBox.text.replace(/\r/g, "\n");
                if (!lyrics || lyrics.replace(/\s+/g, "").length === 0) {
                    alert("Paste some lyrics so we know how many words to map.");
                    return;
                }

                var words = lyrics.split(/\s+/).filter(function (w) { return w.length > 0; });
                if (words.length === 0) {
                    alert("No words detected in the lyrics.");
                    return;
                }

                var peaks = findPeaks(slider, threshold, spacing);
                if (peaks.length === 0) {
                    alert("No peaks found above the threshold. Try lowering the threshold or spacing.");
                    return;
                }

                var pairCount = Math.min(words.length, peaks.length);
                var textLayer = ensureTextLayer(activeComp, "Lyric Line");

                createLyricMarkers(layer, peaks, words, pairCount);
                keyframeLyrics(textLayer, peaks, words, pairCount);

                reportResults(words.length, peaks.length, pairCount);
            } finally {
                app.endUndoGroup();
            }
        };

        palette.layout.layout(true);
        palette.onResizing = palette.onResize = function () { this.layout.resize(); };
        return palette;
    }

    function populateAudioDropdown(dropdown) {
        dropdown.removeAll();
        var comp = app.project && app.project.activeItem && (app.project.activeItem instanceof CompItem) ? app.project.activeItem : null;
        if (!comp) {
            return;
        }

        for (var i = 1; i <= comp.numLayers; i++) {
            var layer = comp.layer(i);
            if (layer.nullLayer || layer.hasAudio || hasAudioAmplitudeEffect(layer)) {
                var item = dropdown.add("item", layer.name);
                item.layerRef = layer;
            }
        }
        if (dropdown.items.length > 0) {
            dropdown.selection = 0;
        }
    }

    function hasAudioAmplitudeEffect(layer) {
        if (!layer.property("Effects")) { return false; }
        var effect = layer.property("Effects").property("Both Channels");
        return !!effect && !!effect.property("Slider");
    }

    function findAudioAmplitudeSlider(layer) {
        if (!layer.property("Effects")) { return null; }
        var both = layer.property("Effects").property("Both Channels");
        if (both && both.property("Slider")) {
            return both.property("Slider");
        }
        var left = layer.property("Effects").property("Left Channel");
        if (left && left.property("Slider")) {
            return left.property("Slider");
        }
        var right = layer.property("Effects").property("Right Channel");
        if (right && right.property("Slider")) {
            return right.property("Slider");
        }
        return null;
    }

    function findPeaks(slider, threshold, spacing) {
        var peaks = [];
        var lastTime = -spacing;
        var numKeys = slider.numKeys;
        if (numKeys === 0) {
            return peaks;
        }

        for (var i = 1; i <= numKeys; i++) {
            var value = slider.keyValue(i);
            var time = slider.keyTime(i);
            if (value >= threshold && (time - lastTime) >= spacing) {
                var localMax = value;
                var localTime = time;
                if (i < numKeys) {
                    var nextValue = slider.keyValue(i + 1);
                    if (nextValue > localMax) {
                        localMax = nextValue;
                        localTime = slider.keyTime(i + 1);
                    }
                }
                peaks.push({ time: localTime, value: localMax });
                lastTime = localTime;
            }
        }
        return peaks;
    }

    function ensureTextLayer(comp, name) {
        var layer = null;
        for (var i = 1; i <= comp.numLayers; i++) {
            if (comp.layer(i).name === name && comp.layer(i) instanceof TextLayer) {
                layer = comp.layer(i);
                break;
            }
        }
        if (!layer) {
            layer = comp.layers.addText("");
            layer.name = name;
        }
        return layer;
    }

    function createLyricMarkers(layer, peaks, words, count) {
        var markerProp = layer.property("Marker");
        if (!markerProp) { return; }
        markerProp.removeAll();
        for (var i = 0; i < count; i++) {
            var marker = new MarkerValue(words[i]);
            markerProp.setValueAtTime(peaks[i].time, marker);
        }
    }

    function keyframeLyrics(textLayer, peaks, words, count) {
        var sourceText = textLayer.property("Source Text");
        if (!sourceText) { return; }
        sourceText.setValueAtTime(0, new TextDocument(""));
        for (var i = 0; i < count; i++) {
            sourceText.setValueAtTime(peaks[i].time, new TextDocument(words[i]));
        }
        if (count > 0) {
            var lastIndex = count - 1;
            sourceText.setValueAtTime(peaks[lastIndex].time + 0.01, new TextDocument(words[lastIndex]));
        }
    }

    function reportResults(wordCount, peakCount, mapped) {
        var message = "Words: " + wordCount + "\n";
        message += "Detected peaks: " + peakCount + "\n";
        message += "Mapped: " + mapped + "\n";
        if (peakCount < wordCount) {
            message += "Not enough peaks to cover every word. Try lowering the threshold or spacing.";
        } else if (peakCount > wordCount) {
            message += "Extra peaks found; only the first " + mapped + " were used.";
        } else {
            message += "All words mapped to detected peaks.";
        }
        alert(message);
    }

    var ui = buildUI(thisObj);
    if (ui instanceof Window) {
        ui.center();
        ui.show();
    }
})(this);
