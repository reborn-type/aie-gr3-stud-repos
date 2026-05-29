import styles from './Appeal.module.css'
import deleteIcn from '@public/delete_icn.svg';

const departmentLabels = {
    PAYMENT_OUT_FAIL: 'Отдел платежей и переводов',
    INCOMING_DELAY: 'Отдел входящих зачислений',
    APP_LOGIN: 'Отдел доступа к приложению',
    CARD_ISSUE: 'Отдел банковских карт',
    ACCOUNT_SEIZED: 'Отдел блокировок и ограничений',
    FRAUD_SUSPECTED: 'Отдел финансовой безопасности',
    KYC_VERIFICATION: 'Отдел идентификации клиентов',
    APP_TECH: 'Отдел технической поддержки приложения',
};

const Appeal = ({appeal, onDelete}) => {
    const confidence = Number(appeal.percent_of_confidence).toFixed(2);
    const departmentName = departmentLabels[appeal.department] ?? appeal.department;

    return(
        <div>
            <div className={styles.appeal__container}>
                <div className={styles.appeal__header}>
                    <h2 className={styles.appeal__title}>{appeal.title}</h2>
                    <button
                        type="button"
                        className={styles.delete__container}
                        onClick={() => onDelete(appeal.id)}
                        aria-label="Удалить обращение"
                    >
                        <img src={deleteIcn} alt="icon" className={styles.delete_icn}/>
                    </button>
                </div>
                <div className={styles.appeal__conent}>
                    <p className={styles.appeal__text}>{appeal.text}</p>
                </div>
                <div className={styles.appeal__department}>
                    <p className={styles.department__name}>{departmentName}</p>
                    <p className={styles.department__confidance}>{confidence}%</p>
                </div>
            </div>
        </div>
    )
}

export default Appeal;
