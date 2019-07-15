import { autoinject } from "aurelia-framework";
import { StylesCalculator } from "./styles-calculator";

@autoinject
export class GoodScrollIntoViewIfCustomAttribute {
    private _element: Element;
    private _retryCount: number = 0;

    private _stylesCalculator: StylesCalculator;

    public constructor(element: Element) {
        this._element = element;
        this._stylesCalculator = new StylesCalculator();
    }

    public valueChanged(newValue: boolean, oldValue: boolean): void {
        if (newValue) {
            let element = this._element as HTMLElement;
            if (element == undefined) {
                return;
            }

            let parentElement = this._element.parentElement;
            if (parentElement == undefined) {
                // the element most likely has not yet been attached to the parent => retrying once is enough to resolve this
                this._retryCount++;
                if (this._retryCount > 1) {
                    // something's wrong, maybe next time... :/
                    this._retryCount = 0;
                    return;
                }

                setTimeout((): void => this.valueChanged(newValue, oldValue), 10);
                return;
            }

            this._retryCount = 0;
            this.scrollIntoView(element, parentElement);
        }
    }

    private scrollIntoView(element: HTMLElement, parentElement: HTMLElement): void {
        let itemRect = element.getBoundingClientRect();
        let desiredOffsetUp = 0;
        let desiredOffsetDown = parentElement.scrollHeight;

        let nextSibling = element.nextElementSibling;
        if (nextSibling != undefined) {
            let siblingRect = nextSibling.getBoundingClientRect();
            let distanceToNext = siblingRect.top - (itemRect.top + itemRect.height);
            desiredOffsetDown = element.offsetTop + itemRect.height + distanceToNext;
        }

        let previousSibling = element.previousElementSibling;
        if (previousSibling != undefined) {
            let siblingRect = previousSibling.getBoundingClientRect();
            let distanceToPrevious = itemRect.top - (siblingRect.top + siblingRect.height);
            desiredOffsetUp = element.offsetTop - distanceToPrevious;
        }

        if  (desiredOffsetUp < parentElement.scrollTop) {
            parentElement.scrollTop = desiredOffsetUp;
        }
        else if (desiredOffsetDown > parentElement.scrollTop + parentElement.offsetHeight) {
            parentElement.scrollTop = desiredOffsetDown - parentElement.offsetHeight;
        }
    }
}
