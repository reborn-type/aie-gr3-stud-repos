import Appeal from "../components/Appeal/Appeal";
import styles from "./IndexPage.module.css";
import { useEffect, useState } from "react";

import { api } from '../shared/api/axios';


const IndexPage = () => {

    const [errors, setErrors] = useState({});
    const [title, setTitle] = useState('');
    const [text, setText] = useState('');
    const [appeals, setAppeals] = useState([]);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const isRequired = (value) => value.trim().length > 0;

    const clearFieldError = (fieldName) => {
        setErrors((prevErrors) => {
            const nextErrors = { ...prevErrors };
            delete nextErrors[fieldName];
            return nextErrors;
        });
    };

    const validateForm = () => {

        const newErrors = {};

        if (!isRequired(title)) {
            newErrors.title = 'Введите заголовок обращения';
        }

        if (!isRequired(text)) {
            newErrors.text = 'Введите текст обращения';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    useEffect(() => {
        api.getAppeals()
            .then((data) => {
                setAppeals(data);
            })
            .catch((error) => {
                console.error('Ошибка загрузки обращений:', error);
            });
    }, []);

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!validateForm()) {
            return;
        }

        if (isSubmitting) {
            return;
        }

        const newAppeal = {
            title,
            text,
        };

        try {
            setIsSubmitting(true);
            const savedAppeal = await api.createAppeal(newAppeal);

            setAppeals((prevAppeals) => [...prevAppeals, savedAppeal]);
            setTitle('');
            setText('');
        } catch (error) {
            console.error('Ошибка создания обращения:', error);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleDelete = async (appealId) => {
        setAppeals((prevAppeals) => (
            prevAppeals.filter((appeal) => appeal.id !== appealId)
        ));

        try {
            await api.deleteAppeal(appealId);
        } catch (error) {
            console.error('Ошибка удаления обращения:', error);
        }
    };


    return (
        <div className={styles.index_page}>
            <div className={styles.page__top_section}>
                <h1 className={styles.page__header}>Добро пожаловать в классификатор обращений!</h1>
            </div>
            <div className={styles.add_appeal__section}>
                <div>
                    <h2 className={styles.add_appeal__title}>Здесь вы можете создать обращение:</h2>
                </div>
                <form onSubmit={handleSubmit}>
                    <div className={styles.input_wrapper}>
                        <p className={styles.input_title}>Заголовок:</p>
                        <input
                            type="text"
                            placeholder="Введите заголовок"
                            className={styles.title_input}
                            value={title}
                            onChange={(event) => {
                                setTitle(event.target.value);
                                clearFieldError('title');
                            }}
                        />
                        {errors.title && <p className={styles.error_text}>{errors.title}</p>}
                    </div>
                    <div className={styles.input_wrapper}>
                        <p className={styles.input_title}>Содержание</p>
                        <textarea
                            placeholder="Введите текст"
                            className={styles.text_input}
                            value={text}
                            onChange={(event) => {
                                setText(event.target.value);
                                clearFieldError('text');
                            }}
                        />
                        {errors.text && <p className={styles.error_text}>{errors.text}</p>}
                    </div>
                    <div className={styles.button_wrapper}>
                        <button type="submit" className={styles.submit_btn} disabled={isSubmitting}>
                            {isSubmitting ? 'Отправка...' : 'Отправить'}
                        </button>
                        <button type="button"
                        className={styles.cancel_btn}
                        onClick={() => {
                            setTitle('');
                            setText('');
                            setErrors({});
	                        }}>Отменить</button>
                    </div>
                </form>
            </div>
            <div className={styles.appeal_list}>
                {appeals.map((appeal) => (
                    <Appeal 
                        key={appeal.id}
                        appeal={appeal}
                        onDelete={handleDelete}
                    />
                ))}
            </div>
        </div>
    )
}

export default IndexPage;
