import { Example } from "./Example";

import styles from "./Example.module.css";

export type ExampleModel = {
    text: string;
    value: string;
};

const EXAMPLES: ExampleModel[] = [
    {
        text: "Qual o EBITIDA do B2B no 4t21?",
        value: "Qual o EBITIDA do B2B no 4t21?"
    },
    { text: "Qual foi o resultado da BR Mania em 2022?", value: "Qual foi o resultado da BR Mania em 2022?" },
    { text: "Qual o volume de vendas no 2t22?", value: "Qual o volume de vendas no 2t22?" }
];

interface Props {
    onExampleClicked: (value: string) => void;
}

export const ExampleList = ({ onExampleClicked }: Props) => {
    return (
        <ul className={styles.examplesNavList}>
            {EXAMPLES.map((x, i) => (
                <li key={i}>
                    <Example text={x.text} value={x.value} onClick={onExampleClicked} />
                </li>
            ))}
        </ul>
    );
};
