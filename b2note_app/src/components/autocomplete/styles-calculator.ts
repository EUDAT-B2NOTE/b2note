import { Thicknesses } from "./thicknesses";

export class StylesCalculator {
    public computeMargins(element: HTMLElement): Thicknesses {
        let styles = window.getComputedStyle(element);
        let result = new Thicknesses();
        result.left = parseInt(styles.marginLeft ? styles.marginLeft : "0", 10);
        result.top = parseInt(styles.marginTop ? styles.marginTop : "0", 10);
        result.right = parseInt(styles.marginRight ? styles.marginRight : "0", 10);
        result.bottom = parseInt(styles.marginBottom ? styles.marginBottom : "0", 10);
        return result;
    }

    public computePaddings(element: HTMLElement): Thicknesses {
        let styles = window.getComputedStyle(element);
        let result = new Thicknesses();
        result.left = parseInt(styles.paddingLeft ? styles.paddingLeft : "0", 10);
        result.top = parseInt(styles.paddingTop ? styles.paddingTop : "0", 10);
        result.right = parseInt(styles.paddingRight ? styles.paddingRight : "0", 10);
        result.bottom = parseInt(styles.paddingBottom ? styles.paddingBottom : "0", 10);
        return result;
    }

    public computeBorderSizes(element: HTMLElement): Thicknesses {
        let styles = window.getComputedStyle(element);
        let result = new Thicknesses();
        result.left = parseInt(styles.borderLeft ? styles.borderLeft : "0", 10);
        result.top = parseInt(styles.borderTop ? styles.borderTop : "0", 10);
        result.right = parseInt(styles.borderRight ? styles.borderRight : "0", 10);
        result.bottom = parseInt(styles.borderBottom ? styles.borderBottom : "0", 10);
        return result;
    }
}
