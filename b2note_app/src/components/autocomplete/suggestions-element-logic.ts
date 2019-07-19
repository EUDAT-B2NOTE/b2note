import { StylesCalculator } from "./styles-calculator";
import { Thicknesses } from "./thicknesses";

export class SuggestionsElementLogic {
    public inputElement: HTMLElement;
    public suggestionsElement: HTMLElement;

    private _stylesCalculator: StylesCalculator;

    public constructor() {
        this._stylesCalculator = new StylesCalculator();
    }

    public get areSuggestionsHidden(): boolean {
        return this.suggestionsElement.style.display === "none";
    }

    public showSuggestions(): void {
        let inputRect = this.inputElement.getBoundingClientRect();
        let inputMargins = this._stylesCalculator.computeMargins(this.inputElement);
        let inputDisplayStyle = window.getComputedStyle(this.inputElement).display;

        this.updateVerticalDimensions(inputRect, inputMargins, inputDisplayStyle);
        this.updateHorizontalDimensions(inputRect, inputMargins);
        this.suggestionsElement.style.display = "block";
    }

    public hideSuggestions(): void {
        this.suggestionsElement.style.display = "none";
    }

    private updateVerticalDimensions(inputRect: ClientRect, inputMargins: Thicknesses, inputDisplayStyle: string | null): void {
        this.suggestionsElement.style.top = null;
        this.suggestionsElement.style.bottom = null;
        this.suggestionsElement.style.maxHeight = null;
        this.suggestionsElement.classList.remove('gac-suggestions-up');
        this.suggestionsElement.classList.add('gac-suggestions-down');

        let computedStyle = window.getComputedStyle(this.suggestionsElement);
        let suggestionsMarginBottom = parseInt(computedStyle.marginBottom || "16", 10);
        let suggestionsMaxHeight = parseInt(computedStyle.maxHeight || "0", 10);

        let topMarginToConsider = inputDisplayStyle === "block" ? 0 : inputMargins.top;
        //let newMaxHeight = window.innerHeight - inputRect.top - inputRect.height - this.suggestionsBottomMargin;
        let newMaxHeight = window.innerHeight - inputRect.top - inputRect.height - suggestionsMarginBottom;
        if (suggestionsMaxHeight > 0) {
            newMaxHeight = Math.min(newMaxHeight, suggestionsMaxHeight);
        }

        if (newMaxHeight < 100) {
            this.suggestionsElement.classList.remove('gac-suggestions-down');
            this.suggestionsElement.classList.add('gac-suggestions-up');
            
            // calculate new max height (upwards)
            computedStyle = window.getComputedStyle(this.suggestionsElement);
            let suggestionsMarginTop = parseInt(computedStyle.marginTop || "16", 10);
            suggestionsMaxHeight = parseInt(computedStyle.maxHeight || "0", 10);
            newMaxHeight = inputRect.top - suggestionsMarginTop;
            
            if (suggestionsMaxHeight > 0) {
                newMaxHeight = Math.min(newMaxHeight, suggestionsMaxHeight);
            }

            let bottom = inputRect.height - topMarginToConsider;
            if (this.inputElement.parentElement != undefined) {
                // if there are line-breaks or similar after the input element, it's not sufficient to take the input element's height only
                bottom = this.inputElement.parentElement.getBoundingClientRect().height - topMarginToConsider;
            }
            
            this.suggestionsElement.style.bottom = bottom + "px";            
        }

        this.suggestionsElement.style.maxHeight = newMaxHeight + "px";
    }

    private updateHorizontalDimensions(inputRect: ClientRect, inputMargins: Thicknesses): void {
        this.suggestionsElement.style.left = inputMargins.left + "px";
        this.suggestionsElement.style.minWidth = inputRect.width + "px";
    }
}
