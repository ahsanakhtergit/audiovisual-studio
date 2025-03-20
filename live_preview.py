import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";

const TemplateDesigner = () => {
  const [textColor, setTextColor] = useState("#ffffff");
  const [fontSize, setFontSize] = useState(1);
  const [fontFamily, setFontFamily] = useState("Arial");
  const [outlineColor, setOutlineColor] = useState("#000000");
  const [outlineThickness, setOutlineThickness] = useState(1);
  const [shadowColor, setShadowColor] = useState("#000000");
  const [shadowOpacity, setShadowOpacity] = useState(0.5);
  const [textAlignment, setTextAlignment] = useState("center");
  const [backgroundColor, setBackgroundColor] = useState("#000000");
  const [backgroundOpacity, setBackgroundOpacity] = useState(0);
  const [highlightColor, setHighlightColor] = useState("#ff0000");
  const [animationType, setAnimationType] = useState("None");
  const [animationSpeed, setAnimationSpeed] = useState(1.5);

  return (
    <div className="grid grid-cols-3 gap-4 p-4">
      <Card>
        <CardContent>
          <h3 className="text-lg font-semibold">🎨 Text Design</h3>
          <div className="space-y-2">
            <label>Text Color</label>
            <input type="color" value={textColor} onChange={(e) => setTextColor(e.target.value)} />
            <label>Font Size</label>
            <Slider min={0.5} max={2} step={0.01} value={fontSize} onChange={setFontSize} />
            <label>Font Family</label>
            <Select value={fontFamily} onValueChange={setFontFamily}>
              <SelectTrigger><SelectValue placeholder="Select Font" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="Arial">Arial</SelectItem>
                <SelectItem value="Roboto">Roboto</SelectItem>
                <SelectItem value="Serif">Serif</SelectItem>
              </SelectContent>
            </Select>
            <label>Outline Color</label>
            <input type="color" value={outlineColor} onChange={(e) => setOutlineColor(e.target.value)} />
            <label>Outline Thickness</label>
            <Slider min={0} max={5} step={1} value={outlineThickness} onChange={setOutlineThickness} />
            <label>Shadow Color</label>
            <input type="color" value={shadowColor} onChange={(e) => setShadowColor(e.target.value)} />
            <label>Shadow Opacity</label>
            <Slider min={0} max={1} step={0.01} value={shadowOpacity} onChange={setShadowOpacity} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <h3 className="text-lg font-semibold">📐 Content Positioning</h3>
          <label>Text Alignment</label>
          <Select value={textAlignment} onValueChange={setTextAlignment}>
            <SelectTrigger><SelectValue placeholder="Select Alignment" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="left">Left</SelectItem>
              <SelectItem value="center">Center</SelectItem>
              <SelectItem value="right">Right</SelectItem>
            </SelectContent>
          </Select>
          <label>Background Color</label>
          <input type="color" value={backgroundColor} onChange={(e) => setBackgroundColor(e.target.value)} />
          <label>Background Opacity</label>
          <Slider min={0} max={1} step={0.01} value={backgroundOpacity} onChange={setBackgroundOpacity} />
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <h3 className="text-lg font-semibold">🎞 Animation Effects</h3>
          <label>Highlight Color</label>
          <input type="color" value={highlightColor} onChange={(e) => setHighlightColor(e.target.value)} />
          <label>Animation Type</label>
          <Select value={animationType} onValueChange={setAnimationType}>
            <SelectTrigger><SelectValue placeholder="Select Animation" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="None">None</SelectItem>
              <SelectItem value="Fade">Fade</SelectItem>
              <SelectItem value="Slide">Slide</SelectItem>
            </SelectContent>
          </Select>
          <label>Animation Speed</label>
          <Slider min={0.5} max={5} step={0.1} value={animationSpeed} onChange={setAnimationSpeed} />
        </CardContent>
      </Card>

      <div className="col-span-3 flex flex-col items-center">
        <h3 className="text-lg font-semibold mb-2">🔍 Live Preview</h3>
        <div className="border border-black w-full h-32 flex items-center justify-center text-lg font-bold" style={{
          color: textColor,
          fontSize: `${fontSize}rem`,
          fontFamily: fontFamily,
          textAlign: textAlignment,
          textShadow: `0px 0px ${shadowOpacity * 10}px ${shadowColor}`,
          WebkitTextStroke: `${outlineThickness}px ${outlineColor}`,
          backgroundColor: backgroundOpacity > 0 ? backgroundColor : "transparent"
        }}>
          Preview should be here
        </div>
      </div>
    </div>
  );
};

export default TemplateDesigner;
