# OnlineFPGA

## 計畫簡介

OnlineFPGA 是由 [Boledu 基金會](https://www.boledu.org/) 為推廣 IC 設計教育所開發的遠端 FPGA 管理系統，配合實體授課教材，提供學生一套可以遠端使用 Xilinx FPGA 的線上服務平台。

透過 OnlineFPGA 系統，使用者可以隨時遠端租用 FPGA，管理員也可以遠端管理所有 FPGA 設備。系統提供 Web/SSH 連線資訊提供線上 FPGA 使用服務，已註冊的使用者可在限期內租用 FPGA，並在選擇的目標開發板上進行設計驗證。

從 2022 年底到 2025 年底，已累計約 600 個註冊使用者、數千次的登入使用。

**OnlineFPGA 管理系統主要特性：**

- 限制每位使用者同時間只能租用一個 FPGA
- 系統有預設的租用時間，超時會強制結束租用
- 使用者可提前歸還 FPGA，或等租期結束後重新租用
- 管理員可透過內部網路對 FPGA 伺服器及 MPSoC 開發板進行監控與管理

> **注意：** 後續範例以目前 Boledu 基金會運作的 Xilinx U50 / VCK-5K / PYNQ-Z2 / KV260 做說明。若套用到不同的 FPGA 板做管理，可能需要修改部分程式碼。

---

## 基本需求

OnlineFPGA 系統運作涵蓋 3 個部分：

1. **遠端電源控制** — 透過智慧插座遠端管理 FPGA 設備電源
2. **Router 的 Port Forwarding 設置** — 透過單一外網 IP 對應不同 port 連線到各設備
3. **OnlineFPGA 管理伺服器** — 安裝管理系統套件，提供使用者租用與管理功能

---

### 1. 遠端電源控制

以 Boledu 使用的 **Kasa H300 智慧插座**為例，此插座透過 WiFi 對外連線，管理員可以透過 Kasa App 對特定 FPGA 伺服器或 FPGA 開發板進行即時遠端電源重啟，也可設定排程在固定維護時段自動重啟。

下方為 Boledu 設置範例：

- `HLS00` ~ `HLS05`：6 台獨立伺服器各別開關（其中 `HLS00` 為 OnlineFPGA 管理伺服器，`HLS01` ~ `HLS05` 為 FPGA 伺服器）
- `KV260_01-20`：5 個 KV260 MPSoC FPGA 開發板同時開關（一組）
- `PYNQ_01-18`：4 個 PYNQ-Z2 MPSoC FPGA 開發板同時開關（一組）

> KV260 及 PYNQ-Z2 的智慧插座以多個開發板共用一組為單位，可依需求配置多組。

---

### 2. Router 的 Port Forwarding 設置

OnlineFPGA 對外提供一個 IP address，透過 router port forwarding 的不同 port 配置，可各別連線到管理伺服器、FPGA 伺服器及 MPSoC FPGA 開發板。其中伺服器（HLS00 ~ HLS05）透過 SSH 連線，PYNQ-Z2 及 KV260 開發板透過 Jupyter Notebook 服務連線（內部 port 9090）。

以 **ASUS Router** 為例，通常可以在「系統管理 → 系統設定」頁面開啟遠端管理的 8443 Port，管理員就可以遠端透過 `http://<ip_address>:8443` 連線 router，來管理 FPGA 綁定的 port。

以下為 Boledu 的 port 配置範例：

#### Server IP 分配

伺服器透過 SSH 連線，外部使用者以 `ssh <user>@<external_ip> -p <external_port>` 連入（例如 `-p 1000` 連到 HLS00 的 port 22）。

| 名稱 | LAN IP | External Port | Internal Port | AnyDesk |
|:---:|:---:|:---:|:---:|:---:|
| HLS00 | 192.168.1.10 | 1000:1099 | 22 | 100000001 |
| HLS01 | 192.168.1.11 | 1100:1199 | 22 | 100000002 |
| HLS02 | 192.168.1.12 | 1200:1299 | 22 | 100000003 |
| HLS03 | 192.168.1.13 | 1300:1399 | 22 | 100000004 |
| HLS04 | 192.168.1.14 | 1400:1499 | 22 | 100000005 |
| HLS05 | 192.168.1.15 | 1500:1599 | 22 | 100000006 |

> **注意：** 上表是外部連線經 router 的對應。管理伺服器 HLS00 在內網是直接以 `192.168.1.1N:1N00`（HLS01 為 `192.168.1.11:1100`）連到 HLS01 ~ HLS05（`monitord.py` 的 nc / SSH 與 `sync_hlsclient.sh` 的 scp），不經過 router，所以 HLS01 ~ HLS05 的 sshd 除了 22 之外也要監聽 1N00（見 3-2）。

#### PYNQ-Z2 IP 分配

PYNQ-Z2 透過 Jupyter Notebook 服務連線，外部使用者以 `http://<external_ip>:<external_port>` 開啟。

| 名稱 | LAN IP | External Port | Internal Port |
|:---:|:---:|:---:|:---:|
| PYNQ01 | 192.168.1.101 | 20100 | 9090 |
| PYNQ02 | 192.168.1.102 | 20200 | 9090 |
| PYNQ03 | 192.168.1.103 | 20300 | 9090 |
| PYNQ04 | 192.168.1.104 | 20400 | 9090 |
| PYNQ05 | 192.168.1.105 | 20500 | 9090 |
| PYNQ06 | 192.168.1.106 | 20600 | 9090 |
| PYNQ07 | 192.168.1.107 | 20700 | 9090 |
| PYNQ08 | 192.168.1.108 | 20800 | 9090 |
| PYNQ09 | 192.168.1.109 | 20900 | 9090 |
| PYNQ10 | 192.168.1.110 | 21000 | 9090 |
| PYNQ11 | 192.168.1.111 | 21100 | 9090 |
| PYNQ12 | 192.168.1.112 | 21200 | 9090 |
| PYNQ13 | 192.168.1.113 | 21300 | 9090 |
| PYNQ14 | 192.168.1.114 | 21400 | 9090 |
| PYNQ15 | 192.168.1.115 | 21500 | 9090 |
| PYNQ16 | 192.168.1.116 | 21600 | 9090 |
| PYNQ17 | 192.168.1.117 | 21700 | 9090 |
| PYNQ18 | 192.168.1.118 | 21800 | 9090 |

#### KV260 IP 分配

KV260 透過 Jupyter Notebook 服務連線，外部使用者以 `http://<external_ip>:<external_port>` 開啟。

| 名稱 | LAN IP | External Port | Internal Port |
|:---:|:---:|:---:|:---:|
| KV260_01 | 192.168.1.51 | 6100 | 9090 |
| KV260_02 | 192.168.1.52 | 6200 | 9090 |
| KV260_03 | 192.168.1.53 | 6300 | 9090 |
| KV260_04 | 192.168.1.54 | 6400 | 9090 |
| KV260_05 | 192.168.1.55 | 6500 | 9090 |
| KV260_06 | 192.168.1.56 | 6600 | 9090 |
| KV260_07 | 192.168.1.57 | 6700 | 9090 |
| KV260_08 | 192.168.1.58 | 6800 | 9090 |
| KV260_09 | 192.168.1.59 | 6900 | 9090 |
| KV260_10 | 192.168.1.60 | 7000 | 9090 |
| KV260_11 | 192.168.1.61 | 7100 | 9090 |
| KV260_12 | 192.168.1.62 | 7200 | 9090 |
| KV260_13 | 192.168.1.63 | 7300 | 9090 |
| KV260_14 | 192.168.1.64 | 7400 | 9090 |
| KV260_15 | 192.168.1.65 | 7500 | 9090 |
| KV260_16 | 192.168.1.66 | 7600 | 9090 |
| KV260_17 | 192.168.1.67 | 7700 | 9090 |
| KV260_18 | 192.168.1.68 | 7800 | 9090 |
| KV260_19 | 192.168.1.69 | 7900 | 9090 |
| KV260_20 | 192.168.1.70 | 8000 | 9090 |

> **注意：** Router 的 External Port 與 `monitord.py` 中 `fpga_init_db()` 的 port 產生邏輯綁定。若 router 的 External Port 設置與以下規則不同，需修改 `monitord.py` 中對應的程式碼：
>
> | 設備類型 | External Port 產生規則 | 範例 |
> |:---:|:---|:---|
> | PYNQ-Z2 (Jupyter) | `'2' + 設備編號 + '00'` | PYNQ01 → `20100` |
> | KV260 (Jupyter) | `(60 + 設備編號) * 100` | KV260_01 → `6100` |
> | U50 / VCK5K (SSH) | `'1' + 設備編號 + '00'` | U50_01 → `1100` |
>
> U50 / VCK5K 的這個 port 在 `MonitordInLab = True`（預設）時也是 HLS00 內網連線用的 port（`192.168.1.11:1100`）；PYNQ-Z2 / KV260 在內網則固定用 `DefaultSSHPort = 22`。

---

### 3. OnlineFPGA 管理伺服器

在管理伺服器上安裝 OnlineFPGA 管理系統套件後，可以透過內部網路連線對 FPGA 伺服器及 MPSoC FPGA 開發板進行監控及管理，提供使用者進行 FPGA 的線上租用及歸還。

---

## 安裝環境

- **已測試 OS：** Ubuntu 20.04 / 22.04 / 24.04 桌面版
- **程式語言：** Python 3.8 以上版本
- OS 及相依套件版本皆經過 OnlineFPGA 套件的相容性測試，若在不同環境及版本運作，可能會有相容性問題
- 後續設置範例預設 OnlineFPGA 管理系統套件放置於 `/opt/labManageKit` 目錄（在 `config.py`需要設置此路徑）

> **提示：** 安裝測試過程若遇到 Ubuntu sh 腳本不能正常運作，請執行：
> 
> ```bash
> sudo dpkg-reconfigure dash
> ```
> 
> 顯示 GUI 選單後，設定 **dash to No**。

---

## 3-0. 下載 OnlineFPGA 套件

在管理伺服器 HLS00 上，將套件從 GitHub 下載到 `/opt/labManageKit`：

```bash
sudo apt update
sudo apt install -y git
sudo git clone https://github.com/bol-edu/onlinefpga.git /opt/labManageKit
sudo chmod +x /opt/labManageKit/*.sh /opt/labManageKit/utility/*.sh
```

> 後續更新套件可執行 `cd /opt/labManageKit && sudo git pull`。`config.py` 內的 IP、帳號密碼等需依實際環境修改（見 3-5 的 config.py 說明）；若已修改，`git pull` 前請先備份。

## 3-1. 管理伺服器設置
本章節腳本範例中使用 `hls00-passwd` 作為管理伺服器的 sudo 密碼佔位符，實際部署時**務必替換為您自行設定的實際密碼**，並確認腳本中所有出現 `hls00-passwd` 的位置皆已更新（`start_docker_boledudb.sh`、`sync_db.sh`、`sync_onlinefpga.sh`、`utility/cleandb.sh` 及 3-1-8 的 crontab），可用 `grep -rn 'hls00-passwd' /opt/labManageKit` 確認。FPGA 伺服器的 `hls01-passwd` ~ `hls05-passwd` 則在 `sync_hlsclient.sh` 及 `config.py` 的 `U50UserPassWordList` 中替換。

### 3-1-1. 安裝 Docker

```bash
sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
sudo apt install docker-ce
sudo systemctl status docker
```

確認顯示 `active (running)` 狀態表示安裝成功，`Ctrl+C` 跳出。

```bash
sudo usermod -aG docker ${USER}
sudo reboot
```

重開機後執行 `docker ps`，應顯示空的容器列表：

```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

---

### 3-1-2. 安裝 MongoDB 6.0.1 Docker 版

```bash
docker pull mongo:6.0.1
docker images
```

確認顯示 `mongo 6.0.1` 映像檔：

```
REPOSITORY   TAG       IMAGE ID       CREATED       SIZE
mongo        6.0.1     d34d21a9eb5b   3 years ago   693MB
```

---

### 3-1-3. 設置 NAS 伺服器（建議）

NAS 伺服器主要目的是將管理伺服器的 MongoDB 資料做異機儲存及備份，以保障資料的安全。

- **MongoDB 資料路徑：** `/mnt/LabData/hls00/boledudb/`
- **MongoDB 資料備份路徑：** `/opt/labManageKit/backupdb`

> 若沒有設置 NAS 伺服器，則需要修改 MongoDB 資料路徑及備份路徑，修改後也需確認完成 3-1 內所有步驟的安裝及測試。

**a. NAS 伺服器端**

建立與 OnlineFPGA 管理伺服器共用的資料夾（如 `/volume1/LabData`），並設定可被共用的權限。

以 Synology NAS 為例：

1. **控制台 → 共用資料夾 → 編輯 → NFS 權限**，新增規則，客戶端填管理伺服器 HLS00 的內網 IP（如 `192.168.1.10`），設定如下：
   - Squash：不調整
   - 非同步：是
   - 非特殊權限…：允許
   - 交互掛載：允許
2. **File Station → LabData → 建立 `hls00` 資料夾 → 內容 → 權限**，新增 Everyone（類型：允許，權限：讀取）。

**b. OnlineFPGA 管理伺服器端**

```bash
sudo apt update
sudo apt install nfs-common -y
sudo mkdir -p /mnt/LabData
sudo nano /etc/fstab
```

加入以下掛載設定（`192.168.1.2` 為 NAS 伺服器內網位置，請依實際內網配置修改）：

```
192.168.1.2:/volume1/LabData /mnt/LabData nfs defaults 0 0
```

重開機後驗證掛載：

```bash
sudo reboot
df -h
```

看到類似以下資訊代表掛載 NAS 伺服器目錄成功：

```
192.168.1.2:/mnt/LabData     49G   11G 2000G  14% /mnt/LabData
```

建立 MongoDB 資料及備份目錄：

```bash
sudo mkdir -p /mnt/LabData/hls00/boledudb /mnt/LabData/hls00/backupdb
sudo ln -s /mnt/LabData/hls00/backupdb /opt/labManageKit/backupdb
```

**c. 掛載 U50 專案目錄 /mnt/HLSNAS（有 FPGA 伺服器時）**

HLS01 ~ HLS05 的 U50 專案帳號建立在 NAS 的 `/mnt/HLSNAS/`（`config.py` 的 `U50UserHome`）。管理伺服器 HLS00 也要掛載同一個目錄：`monitord.py` 的 `fpga_init` 會讀取 `/mnt/HLSNAS/` 統計各台 U50 的租戶數，`u50_tenant_util.py` 的 `list` / `checkdb` 在 HLS00 執行時也會讀取。

```bash
sudo mkdir -p /mnt/HLSNAS
sudo nano /etc/fstab
```

加入以下掛載設定（NAS 共用目錄請依實際配置修改，HLS01 ~ HLS05 使用相同設定）：

```
192.168.1.2:/volume2/LabData /mnt/HLSNAS nfs defaults 0 0
```

---

### 3-1-4. 啟動 MongoDB 服務

啟動 MongoDB 服務並掛載到 NAS 資料夾：

```bash
docker run -v /mnt/LabData/hls00/boledudb/:/data/db --name boledudb -d mongo:6.0.1
```

確認服務運作：

```bash
docker ps
```

```
CONTAINER ID   IMAGE         COMMAND                  CREATED         STATUS         PORTS       NAMES
172eaab2db40   mongo:6.0.1   "docker-entrypoint.s…"   8 seconds ago   Up 7 seconds   27017/tcp   boledudb
```

確認 DB 資料已建立：

```bash
ls /mnt/LabData/hls00/boledudb/
collection-0--1739418379110125285.wt  diagnostic.data                  index-5--1739418379110125285.wt  _mdb_catalog.wt  storage.bson     WiredTiger.lock
collection-2--1739418379110125285.wt  index-1--1739418379110125285.wt  index-6--1739418379110125285.wt  mongod.lock      WiredTiger       WiredTiger.turtle
collection-4--1739418379110125285.wt  index-3--1739418379110125285.wt  journal                          sizeStorer.wt    WiredTigerHS.wt  WiredTiger.wt
```

---

### 3-1-5. 安裝 MongoDB Compass GUI 工具及連線 MongoDB (建議)

到[官網](https://www.mongodb.com/products/tools/compass)找到最新支援 Ubuntu 64-bit 的版本（以下以 1.49.2 為例）：

```bash
wget https://downloads.mongodb.com/compass/mongodb-compass_1.49.2_amd64.deb
sudo dpkg -i ./mongodb-compass_1.49.2_amd64.deb
```

取得 MongoDB 服務的 Docker 網路位址：

```bash
docker inspect boledudb | grep -A 10 "Networks"
```

找到 `"IPAddress": "172.17.0.2"`，回到管理伺服器的 Ubuntu 桌面，啟動 MongoDB Compass，透過以下 URI 連線：

```
mongodb://172.17.0.2:27017
```

<!-- ![MongoDB Compass 連線](images/mongodb_compass_connect.png) -->
![260301-002](https://github.com/user-attachments/assets/21465623-637f-4062-a08e-0046c74c5f87)

---

### 3-1-6. 建立 MongoDB 的表格及測試 (建議)

在 MongoDB Compass 中：

點選 **Create database**，建立 `boledudb`及 3 個 collections：`boledudevice`、`boledumonitord`、`boleduuser`

<!-- ![建立 database](images/mongodb_create_db.png) -->
![260301-004](https://github.com/user-attachments/assets/f3bac6df-b034-43a6-8191-5648573191e9)

<!-- ![建立 collections](images/mongodb_create_collections.png) -->
![260301-006](https://github.com/user-attachments/assets/06ad89d6-126f-454d-b244-d9577faa6d02)

**MongoDB 寫入及存取測試：**

```bash
sudo apt install python3-pip
python3 -m pip install pymongo
```

建立測試程式 `test.py`：

```python
from pymongo import MongoClient

client = MongoClient("172.17.0.2", 27017)
db = client.boledudb
col_user = db.boleduuser

test_user = {
    "email": "test@example.com",
    "name": "Test User",
    "password": "1234",
    "date": "2026-03-01"
}
col_user.insert_one(test_user)
print("寫入成功")
```

```bash
python3 test.py
# 寫入成功
```

透過 MongoDB Compass 檢視 `boleduuser` 是否有寫入資料，驗證完畢後用 **Remove document** 移除此筆測試資料。
![260301-009](https://github.com/user-attachments/assets/518ae5b6-7b3c-4441-9ccb-107cde04df2a)

---

### 3-1-7. 重開機時自動啟動 MongoDB 服務

管理伺服器定期重開機或不預期重開機時，需自動啟動 MongoDB 服務並掛載到原有 DB 資料。

`start_docker_boledudb.sh` 腳本會在每次重開機時先備份最新 MongoDB 資料再重啟服務。

```bash
#!/bin/bash
echo hls00-passwd | sudo -S rm -rf "/opt/labManageKit/backupdb/$(date +"%Y-%m-%d")"
echo hls00-passwd | sudo -S mkdir "/opt/labManageKit/backupdb/$(date +"%Y-%m-%d")"
echo hls00-passwd | sudo -S cp -rf /mnt/LabData/hls00/boledudb "/opt/labManageKit/backupdb/$(date +"%Y-%m-%d")"
sleep 10
docker rm -f boledudb
docker run -v /mnt/LabData/hls00/boledudb/:/data/db --name boledudb -d mongo:6.0.1
```

> 若資料備份路徑不為範例預設的/mnt/LabData/hls00/backupdb/，後續`sync_db.sh` 腳本的路徑也要修改

設置重開機後自動執行：

```bash
sudo cp -i /opt/labManageKit/start_docker_boledudb.sh /bin
sudo crontab -e
```

加入以下排程，每日備份的 DB 資料會以日期為目錄名稱存放於 `/mnt/LabData/hls00/backupdb/`：

```
@reboot sh /bin/start_docker_boledudb.sh &
```

另外，為避免備份資料持續累積導致磁碟空間不足，`utility/cleandb.sh` 腳本每次執行會保留最新 27 個（`KEEP_BACKUPS`-1）日期備份目錄，並自動刪除較舊的備份目錄。

> 若備份路徑不為預設的 `/mnt/LabData/hls00/backupdb/`，請修改腳本中 `BACKUP_DIRS` 的路徑。
> 若需調整保留份數，請修改 `KEEP_BACKUPS` 的數值（實際保留 `KEEP_BACKUPS`-1 個）。
> 腳本中的 `hls00-passwd` 為範例密碼，請替換為實際設定的管理伺服器 sudo 密碼。

設置每日 06:20 自動執行（早於 06:25 的管理伺服器重啟，重啟後 `start_docker_boledudb.sh` 會再建立當日備份）。使用 hls00 使用者的 crontab（不加 sudo）：

```bash
crontab -e
```

加入以下排程：

```
20 6 * * * /opt/labManageKit/utility/cleandb.sh
```

舊備份目錄將依照日期名稱排序後，從最舊的開始刪除，直到只剩最新 `KEEP_BACKUPS`-1 個為止。

---

### 3-1-8. 設定管理伺服器每日重啟時間

使用 hls00 使用者的 crontab（不加 sudo）：

```bash
crontab -e
```

加入以下排程，設定管理伺服器每日固定重啟時間（例如每日 6:25）：

```
25 6 * * * echo hls00-passwd | sudo -S reboot
```

### 3-1-9. 設定 monitord 開機自動啟動

管理伺服器 HLS00 每日維護重啟後，會在 Ubuntu 桌面自動啟動 Terminal 執行 `start_monitord.sh`，Terminal 會顯示 `monitord.py` 的所有活動 log。

> **注意：** Startup Application 要在桌面登入後才會執行，管理伺服器 HLS00 必須設置 hls00 帳號自動登入，否則重啟後 monitord 不會啟動。

設置自動登入：**Settings → Users → Unlock → Automatic Login** 開啟。或編輯 `/etc/gdm3/custom.conf`，在 `[daemon]` 下加入：

```
AutomaticLoginEnable=true
AutomaticLogin=hls00
```

在 Ubuntu 桌面的 **Startup Application**（每日重啟後自動執行）新增項目：

- **Name：** Monitord
- **Command：** `gnome-terminal -- "/opt/labManageKit/start_monitord.sh"`
- **Comment：** OnlineFPGA Monitord

![2601026-001](https://github.com/user-attachments/assets/8c323551-647d-421a-8036-da099ce68215)

![2601026-002](https://github.com/user-attachments/assets/e72f5880-01d9-4d80-ae55-493b4dee3807)

> `start_monitord.sh` 的內容請見 3-5 的 `start_monitord.sh`。

### 3-1-10. Troubleshooting：MongoDB 無法啟動（管理伺服器非正常斷電後）

管理伺服器非正常斷電/關機後重開機，MongoDB 資料庫目錄 `/mnt/LabData/hls00/boledudb/` 殘留鎖定狀態，`boledudb` 容器無法正常啟動，OnlineFPGA 連不到資料庫，使用者登入失敗。

1. 確認狀況：

```bash
docker ps -a
docker logs boledudb
```

`boledudb` 容器為 Exited，或日誌顯示資料庫無法開啟，繼續下列步驟。

2. 修復前先保留一份資料（修復會修改資料目錄）：

```bash
sudo cp -a /mnt/LabData/hls00/boledudb /mnt/LabData/hls00/backupdb/before_repair
```

> `start_docker_boledudb.sh` 開機時已先備份到 `backupdb/` 的當日目錄（同日備份會被覆蓋，內容可能已是鎖定狀態的資料；前一日的備份仍保留）。`before_repair` 不是日期名稱，`cleandb.sh` 不會清理，確認修復後正常請手動刪除。

3. 執行修復腳本並重新啟動 MongoDB：

```bash
cd /opt/labManageKit/utility
sudo chmod +x *.sh
./fix_mongodb.sh
../start_docker_boledudb.sh
docker ps
```

`docker ps` 顯示 `boledudb` 為 Up 即可重新登入。

---

## 3-2. FPGA 伺服器設置

> 若沒有配置 FPGA 伺服器可忽略此章節。

**安裝環境：** Ubuntu 20.04.5，並已安裝 Vitis 2022.1、XRT 及 U50 套件。

Vitis/XRT 設定檔案範例路徑（若系統安裝路徑不同，需對應修改 3-2-1 的 `.bashrc` 樣板）：

```
/opt/Xilinx/Vitis/2022.1/settings64.sh
/opt/xilinx/xrt/setup.sh
```

請先測試 HLS01 ~ HLS05 FPGA 伺服器在不透過管理系統的情況下，也能正常運作 Vitis/XRT 及存取 FPGA。

**其他前置條件：**

- 主機名稱需為 `HLS01` ~ `HLS05`，管理帳號為 `hls01` ~ `hls05`。`manage_user.py` 及 `u50_tenant_util.py` 由 hostname 取得編號，再到 `config.py` 的 `U50UserPassWordList` 找出含該編號的密碼，所以各台的 sudo 密碼字串需包含自己的編號（例如 `hls01-passwd` 含 `01`）。
- 需有 `docker` 群組：`manage_user.py` 會把 U50 專案帳號加入 `render` 及 `docker` 群組（`config.py` 的 `U50DevGroup`、`U50DockerGroup`）。已安裝 Docker 即有此群組，否則執行 `sudo groupadd docker`。
- sshd 需同時監聽 22（外部經 router `1N00:1N99 → 22` 連入）及 1N00（HLS00 在內網直接連線，見「Server IP 分配」的注意事項）。以 HLS01 為例，在 `/etc/ssh/sshd_config` 加入以下兩行後執行 `sudo systemctl restart ssh`：

```
Port 22
Port 1100
```

- 掛載 NAS 到 `/mnt/HLSNAS`（設定方式同 3-1-3 c）。

---

### 3-2-1. .bashrc 樣板

在 HLS01 ~ HLS05 FPGA 伺服器上執行：

```bash
sudo vim /etc/skel/.bashrc
```

將下方 source Vitis/XRT 的 shell scripts 加入到 `.bashrc` 最後，使每個新建立的使用者（租戶）登入時都會自動 source Vitis/XRT：

```bash
#source Xilinx Vitis/XRT
if [[ -z $XILINX_VITIS ]]; then
    source /opt/Xilinx/Vitis/2022.1/settings64.sh
fi
if [[ -z $XILINX_XRT ]]; then
    source /opt/xilinx/xrt/setup.sh
fi
```

---

### 3-2-2. FPGA 存取權限

在 HLS01 ~ HLS05 FPGA 伺服器上：

```bash
sudo vim /etc/rc.local
```

設定 FPGA 存取權限，使一般使用者（租戶）都可以讀寫。Ubuntu 20.04 預設沒有 `/etc/rc.local`，新建檔案時第一行需為 `#!/bin/bash`、最後一行為 `exit 0`：

```bash
#!/bin/bash
chmod o=rw /dev/dri/render*
exit 0
```

設為可執行後，systemd 的 `rc-local` 服務會在每次開機時執行：

```bash
sudo chmod +x /etc/rc.local
```

---

### 3-2-3. 複製 manage_user.py 及 job_grabber.py 到 FPGA 伺服器

手動在 HLS01 ~ HLS05 建立目錄並複製檔案：

```bash
sudo mkdir -p /opt/labManageKit
sudo chown $USER /opt/labManageKit    # 讓 hlsNN 帳號可由 HLS00 scp 寫入
```

將管理伺服器上的 `config.py`、`manage_user.py`、`job_grabber.py` 及 `u50_tenant_util.py` 複製到各 FPGA 伺服器的 `/opt/labManageKit/` 目錄。

- 管理伺服器會透過 FPGA 伺服器上的 `manage_user.py` 建立使用者帳戶
- 管理伺服器會透過 FPGA 伺服器上的 `job_grabber.py` 配置背景批次工作
- `config.py` 提供 FPGA 伺服器所需的系統參數
- `u50_tenant_util.py` 的 `list` 及 `del` 指令需在各 FPGA 伺服器上直接執行，用於查詢及刪除該伺服器上的 U50 專案帳號

> 後續可使用 `sync_hlsclient.sh` 腳本批次同步上述檔案到所有 FPGA 伺服器。

---

### 3-2-4. 設定 FPGA 伺服器每日重啟時間

在 HLS01 ~ HLS05 FPGA 伺服器上，執行 `crontab -e` 設定每日重啟時間。例如 HLS01：

```
35 6 * * * echo hls01-passwd | sudo -S reboot
```

HLS02 ~ HLS05 也是重複上述設置方式，每台伺服器可設定不同的重啟分鐘數（建議錯開以避免同時重啟造成電力負擔）。

---

## 3-3. MPSoC FPGA 開發板設置

目前 PYNQ-Z2 及 KV260 開發板安裝的映像檔都是使用 **PYNQ 2.7** 環境。管理系統透過派送 `reset_pynq.py` 到指定的 PYNQ-Z2 / KV260 來重啟 Jupyter Notebook 並設置新的登入密碼，強制使用者租期到後登出。

> **建議：** 若沒有特定實驗版本相依，建議安裝 PYNQ 2.7 環境。較新 PYNQ 版本預計會需要修改 `config.py` 及 `reset_pynq.py`。

**驗證 PYNQ 環境：**

```bash
# PYNQ-Z2
ssh xilinx@192.168.1.103
python3 -c "import pynq; print(pynq.__version__)"
# 2.7.0

# KV260
ssh ubuntu@192.168.1.52
python3 -c "import pynq; print(pynq.__version__)"
# 2.7.0
```

**config.py 中 PYNQ-Z2 / KV260 相關參數：**

| 參數  | PYNQ-Z2 | KV260 |
| --- | --- | --- |
| 使用者名稱 | `PynqUserName = 'xilinx'` | `Kv260UserName = 'ubuntu'` |
| 密碼  | `PynqUserPasswd = 'xilinx'` | `Kv260UserPasswd = 'boledukv260'` |
| SSH 登入目錄 | `PynqZ2Home = '/home/xilinx/'` | `Kv260Home = '/home/ubuntu/'` |
| Python3 路徑 | `PynqPython3 = '/usr/local/share/pynq-venv/bin/python3'` | 同左  |
| Jupyter 工作目錄 | `/home/xilinx/jupyter_notebooks/` | `/home/root/jupyter_notebooks/` |

上述參數是提供給 `monitord.py` 用來連線及啟動 `reset_pynq.py` 使用。

> **注意：** `reset_pynq.py` 內的 sudo 指令使用佔位符 `PYNQ_PASSWD` / `KV260_PASSWD`（例如 `echo PYNQ_PASSWD | sudo -S ...`）。`monitord.py` 派送時由 `fill_reset_pynq()` 讀取 `reset_pynq.py`，換成 `config.py` 的 `PynqUserPasswd` / `Kv260UserPasswd` 後直接寫到開發板，所以映像檔的密碼不同時只需修改 `config.py`，`reset_pynq.py` 保持佔位符即可。

**reset_pynq.py 執行流程：**

```
python reset_pynq.py <password|random> <pynq|kv260>
 │
 ├─ 參數不足 → 印錯誤訊息並結束
 │
 ├─ 取得密碼參數
 │     └─ 若為 'random' → 產生 6 位隨機英文字母密碼
 │
 ├─ 確認 PYNQ 版本
 │     ├─ 2.7 → 產生雜湊密碼，寫入 jupyter_notebook_config.json
 │     └─ unknown → 印錯誤並結束
 │
 ├─ 依 board 類型設定路徑與指令
 │     ├─ pynq  → /home/xilinx/jupyter_notebooks/
 │     └─ kv260 → /home/root/jupyter_notebooks/
 │
 ├─ 清理 jupyter_notebooks 目錄
 │     └─ 刪除不在 RemoveExcept 清單內的資料夾/檔案
 │
 └─ 依序執行重啟指令
       ├─ pkill jupyter-notebook（停止服務）
       ├─ mv jupyter_notebook_config.json → /root/.jupyter/（套用新密碼）
       └─ start_jupyter.sh（重新啟動服務）
```

> **PYNQ 3.x 注意事項：** 若使用 PYNQ 3.x，其 Jupyter Notebook 服務、雜湊密碼檔案路徑或檔案格式可能與 PYNQ 2.7 不同，會需要修改 `config.py` 及 `reset_pynq.py`。

---

## 3-4. OnlineFPGA 系統的使用者介面

OnlineFPGA 系統在管理伺服器 HLS00 上提供使用者入口帳號，使用者透過 SSH 連線後會自動進入 OnlineFPGA 選單介面。

**建立使用者入口帳號步驟（以 `boleduuser` 為例）：**

1. 在管理伺服器 HLS00 上建立系統帳戶：

```bash
sudo adduser boleduuser
```

設定密碼為 `boleduuser`（或依需求設定）。

2. 賦予 `boleduuser` sudo 權限，以便安裝相依套件：

```bash
sudo usermod -aG sudo boleduuser
```

3. 切換至 `boleduuser` 帳戶，安裝相依套件：

```bash
su - boleduuser
```

4. 安裝 OnlineFPGA 系統所需的相依套件（Ubuntu 20.04 / 22.04 / 24.04）：

```bash
sudo apt update
sudo apt install -y python3-pip
sudo pip3 install requests pymongo email-validator
```
> **Ubuntu 24.04：** Python 預設版本為 3.12，禁止直接使用 `pip3` 安裝系統層套件，會有 `externally-managed-environment` 錯誤，請改用：
> ```bash
> sudo pip3 install requests pymongo email-validator --break-system-packages
> ```

5. 安裝完成後，離開 `boleduuser` 回到原始帳戶：

```bash
exit
```

6. 編輯使用者的 `.bashrc`，加入歡迎畫面及自動啟動 OnlineFPGA 選單：

```bash
sudo vim /home/boleduuser/.bashrc
```

在 `.bashrc` 末尾加入以下內容（其餘保持 Ubuntu 預設的 shell scripts）：

```bash
Red='\033[0;91m'
Yellow='\033[0;93m'
Blue='\033[0;94m'
Magenta='\033[0;95m'
Reset='\033[0m'
echo -e "\n"
echo -e "${Yellow}######################################################"
echo -e "${Yellow}#                                                    #"
echo -e "${Yellow}#       ${Red}Welcome to BoLedu's OnlineFPGA service       ${Yellow}#"
echo -e "${Yellow}#        ${Blue}Renting OnlineFPGA from service menu        ${Yellow}#"
echo -e "${Yellow}#                                                    #"
echo -e "${Yellow}#       ${Magenta}Shutdown: TPE(UTC+8) 6:00am to 7:00am        ${Yellow}#"
echo -e "${Yellow}#                                                    #"
echo -e "${Yellow}######################################################"
echo -e "${Reset}\n"
python3 onlinefpga.pyc
```

使用者以 SSH 登入後會先看到 `[1] register an BoLedu account`、`[2] already have an account`、`[0] exit OnlineFPGA service` 選單。選 `[1]` 自行註冊時，系統會寄送驗證碼到使用者的 email（需先設定 3-5 `config.py` 的 Gmail 參數）；選 `[2]` 登入後可列出、租用及歸還 PYNQ-Z2 / KV260 / U50 / VCK5K。

7. 編譯 OnlineFPGA 系統程式：

```bash
cd /opt/labManageKit
sudo python3 -m compileall .
```

此命令會檢查所有 Python 檔案的語法正確性，並將編譯後的 `.pyc` 檔案更新到 `__pycache__/` 目錄。

8. 同步編譯後的 `.pyc` 到使用者目錄：

```bash
cd /opt/labManageKit
./sync_onlinefpga.sh
```

`sync_onlinefpga.sh` 會將 `config.pyc` 及 `onlinefpga.pyc` 複製到 `/home/boleduuser/`，並使用 `chattr +i` 鎖定檔案防止使用者竄改。若目標檔案已存在則先解除鎖定再覆蓋，不存在則直接複製。**請依實際 Python 版本修改腳本中的 `cpython-38` 為對應版本號（如 `cpython-310`、`cpython-312`）**，Ubuntu 20.04 / 22.04 / 24.04 預設的 Python 版本各別為 3.8 / 3.10 / 3.12。

```bash
#!/bin/bash
[ -f /home/boleduuser/onlinefpga.pyc ] && echo hls00-passwd | sudo -S chattr -i /home/boleduuser/onlinefpga.pyc
echo hls00-passwd | sudo -S cp -f __pycache__/onlinefpga.cpython-38.pyc /home/boleduuser/onlinefpga.pyc
echo hls00-passwd | sudo -S chattr +i /home/boleduuser/onlinefpga.pyc
[ -f /home/boleduuser/config.pyc ] && echo hls00-passwd | sudo -S chattr -i /home/boleduuser/config.pyc
echo hls00-passwd | sudo -S cp -f __pycache__/config.cpython-38.pyc /home/boleduuser/config.pyc
echo hls00-passwd | sudo -S chattr +i /home/boleduuser/config.pyc
echo "synchronize config.pyc onlinefpga.pyc to OnlineFPGA boleduuser"
```

**BoLedu 提供兩組不同使用者用途帳號：**

| 帳號 | 密碼 | 連線位置 | 可見設備 |
| --- | --- | --- | --- |
| `boleduuser` | `boleduuser` | `<external_ip>:1000` | 所有設備（PYNQ-Z2 / KV260 / U50 / VCK5K），使用本套件的 `onlinefpga.py` |
| `boledupynq` | `boledupynq` | `<external_ip>:1000` | 僅 PYNQ-Z2 及 KV260，需另外客製化 `onlinefpga.py`（見下方說明） |

> **客製化選單：** 若要修改使用者可見設備，需修改 `onlinefpga.py` 再重新編譯後，執行 `sync_onlinefpga.sh` 複製到對應的使用者目錄，視需要修改該使用者的 `.bashrc`。

---

## 3-5. OnlineFPGA 管理系統程式

OnlineFPGA 管理系統開發程式為 Python3，系統程式碼放置於管理伺服器 HLS00 的 `/opt/labManageKit`。程式中使用到的 Python3 相依套件需透過 PIP 安裝，請執行`sudo apt install -y python3-pip`。

### 檔案總覽

| 檔案 / 目錄 | 描述  |
| --- | --- |
| `active_monitord.py` | 激活 monitord 的監控及管理功能 |
| `config.py` | OnlineFPGA 系統參數定義檔案（**需設置 PYNQ-Z2 / KV260 / U50 對應代號、ExternalIP、ExternalIPGateway、GmailSender、GmailPasswd、OnlineFPGAUserManual**） |
| `job_grabber.py` | 支援 batch 功能，使用者提供 Makefile 的 job 列表後，系統自動派送到 HLS 伺服器執行，每個 job 狀態會 email 通知使用者（**需有 FPGA 伺服器**） |
| `list_user.py` | 由資料庫擷取符合指定條件的使用者資料 |
| `manage_dbuser.py` | 建立（支援 CSV 匯入）/ 刪除資料庫中的使用者資料 |
| `manage_user.py` | 派送到 HLS 伺服器後，可建立 / 刪除指定使用者帳戶（**需有 FPGA 伺服器**） |
| `monitord.py` | OnlineFPGA 系統監控及管理主程式 |
| `onlinefpga.py` | OnlineFPGA 系統的使用者選單介面：註冊 / 登入，列出、租用、歸還 PYNQ-Z2 / KV260 / U50 / VCK5K |
| `__pycache__/` | 存放編譯後的 OnlineFPGA 程式 |
| `registration.csv` | CSV 範例檔案用來批次建立使用者資料 |
| `reset_pynq.py` | 派送到 PYNQ-Z2 / KV260 用來重啟 Jupyter Notebook 並設置新的登入密碼（**需修改程式碼，若不是PYNQ 2.7版**） |
| `start_docker_boledudb.sh` | 管理伺服器重啟後備份 MongoDB 資料庫並重啟 Docker（**需設置 sudo 密碼**） |
| `start_monitord.sh` | 啟動 `active_monitord.py` 及 `monitord.py` （**維護時間預設 06:00-07:00，若異動需同步修改腳本內容**）|
| `stop_monitord.sh` | 關閉所有 monitord 相關程序 |
| `sync_db.sh` | 手動備份 MongoDB 資料庫（**需設置 sudo 密碼**） |
| `sync_hlsclient.sh` | 手動同步管理伺服器檔案到 HLS01 ~ HLS05（**需有 FPGA 伺服器**） |
| `sync_onlinefpga.sh` | 手動同步編譯後的 `.pyc` 到使用者目錄（**需設置 sudo 密碼**） |
| `u50_rented.log` | HLS01 ~ HLS05 FPGA 伺服器租用紀錄檔案（**需有 FPGA 伺服器**） |
| `u50_tenant_util.py` | 使用者帳戶工具程式（管理 U50 綁定紀錄與專案帳號）（**需有 FPGA 伺服器**） |
| `utility/cleandb.sh` | 清理HLSNAS的backupdb目錄下較舊的備份，只保留最新27個日期目錄 |
| `utility/fix_mongodb.sh` | HLS00非正常斷電後，修復被鎖定的MongoDB資料庫 (見3-1-10 Troubleshooting) |
| `utility/check_ssh_connection.sh` | 查詢最近的 SSH 連線詳細資料 |
| `utility/list_subdir_size.sh` | 查詢特定目錄下所有子目錄的使用空間（**需手動輸入 sudo 密碼**） |

**安裝 Python3 相依套件：**

```bash
sudo pip3 install paramiko requests apscheduler pymongo email-validator flask
```
>**Ubuntu 24.04：** 避免 `externally-managed-environment` 錯誤，請改用：
>```bash
>sudo pip3 install paramiko requests apscheduler pymongo email-validator flask --break-system-packages
>```

**安裝 Ubuntu 相依套件：**

```bash
sudo apt install -y sshpass mtr-tiny netcat-openbsd
```

> `mtr` 用於 `monitord.py` 判斷目前走的是 `ExternalIP` 或 `ExternalIPBak` 外網；`nc` 用於 U50 / VCK5K 的狀態檢查（`nc -w 5 <ip> <port>`：在 5 秒內連到該 HLS 的 SSH port，有收到 SSH 版本字串即判定伺服器在線）。

> **權限設定：** 執行 `sudo chmod +x /opt/labManageKit/*.sh /opt/labManageKit/utility/*.sh` 使所有 sh 檔案可以直接執行。`/opt/labManageKit` 目錄下有異動檔案時需要 `sudo` 權限。

---

### Python3 的編譯

修改 Python3 檔案後，在管理伺服器 HLS00 的 `/opt/labManageKit` 目錄中執行：

```bash
sudo python3 -m compileall .
```

會檢查異動檔案的語法正確性，並將編譯檔案更新到 `__pycache__/` 目錄。

> **重要：** 修改後需執行 `sync_onlinefpga.sh`（同步使用者介面）或 `sync_hlsclient.sh`（同步 FPGA 伺服器檔案）使修改生效。

---

### 管理系統的維護時間

每天早上 **6:00 到 7:00** 間所有伺服器會自動重啟，PYNQ-Z2 / KV260 會斷電再重開。

---

### 管理員定期維護事項

1. **清理備份：** `backupdb/` 目錄下的備份需定期移除不需要的備份，節省磁碟空間
2. **清理日誌：** `u50_rented.log` 檔案過大時，可複製到 `u50_rented.old01.log` 後再清空檔案內容
3. **清理專案帳號：** 學期結束或專案結束時，需移除 HLS01 ~ HLS05 的 U50 / VCK-5K 專案帳號、對應目錄及管理伺服器的使用者 U50 綁定紀錄

---

### active_monitord.py

**Usage：**

```bash
python3 active_monitord.py fpga_init
python3 active_monitord.py retry_unknown
python3 active_monitord.py retry_available <device>
python3 active_monitord.py run_routine
python3 active_monitord.py run_startup
```

| 指令  | 說明  |
| --- | --- |
| `fpga_init` | 初始化所有 FPGA 設備的管理狀態（可列表設備、可用狀態、內網 IP 等）。管理伺服器於每日維護重啟後自動執行。**在有使用者租用的情況下不建議執行。** |
| `retry_unknown` | 嘗試重新激活顯示為 `unknown` 狀態的設備。最常用於處理 PYNQ-Z2 的 unknown 狀態——先用智慧電源 App 重啟設備實體電源，等約 3 分鐘進入運作後再執行。 |
| `retry_available <device>` | 嘗試重新激活顯示為 `available` 但實際無法使用的設備（用於 PYNQ 設備），例如 `retry_available pynq_05` |
| `run_routine` | 在維護時間外由 `start_monitord.sh` 引用，定期激活 monitord 檢查事件及重試 unknown 設備 |
| `run_startup` | 在維護時間內由 `start_monitord.sh` 引用，先做 `fpga_init` 初始化後再定期檢查 |

> 因 `fpga_init`、`run_routine` 及 `run_startup` 在每天管理伺服器重啟後都會自動運作，管理員通常不會直接使用。最常用的是 `retry_unknown`。

---

### config.py

OnlineFPGA 系統參數定義檔案，大部分參數請使用預設值。異動 `config.py` 後，使參數生效的方法有兩種：

1. **即時生效（在無使用者租用時）：** 依序執行 `stop_monitord.sh` → `start_monitord.sh` → `python3 active_monitord.py fpga_init`
2. **等待每日維護時間自動重啟後生效**

**常用參數設定範例：**

**(1) 租用時間設定**

```python
RentedPynqMinutes = 60       # PYNQ-Z2 預設 60 分鐘
RentedKv260Minutes = 120     # KV260 預設 120 分鐘
RentedU50Minutes = 120       # U50 預設 120 分鐘
RentedVCK5KMinutes = 240     # VCK5K 預設 240 分鐘
```

**(2) 設備清單設定**

管理系統選單出現的設備代號可透過以下參數調整，故障的MPSoC代號可跳過：

```python
PynqZ2List = ['01', '02', '03', '04', '05', '06', '07', '09', '10', '11', '12']    # 依實際可用的板子填寫，故障板可跳過
Kv260List = ['02', '03', '04', '05', '06', '08', '09', '10', '11', '12', '13', '20']
```

> **注意：** 新增 PYNQ-Z2 / KV260 設備時，router 裡也要設定對應的 MAC address 及內網 IP address。

**(3) 新增 FPGA 伺服器**

假設新增 HLS06 伺服器並安裝一個 U50 卡：

```python
U50List = ['01', '02', '03', '04', '05', '06']
U50UserNameList = ['hls01', 'hls02', 'hls03', 'hls04', 'hls05', 'hls06']
U50UserPassWordList = ['hls01-passwd', 'hls02-passwd', 'hls03-passwd',
                       'hls04-passwd', 'hls05-passwd', 'hls06-passwd']
U50BoardAvailable = [1, 1, 1, 1, 1, 1]
U50Alias = ['', '', '', '', 'vck5k_01', '']
```

> HLS06 伺服器設置的管理帳號也要為 `hls06`，sudo 密碼字串需包含編號 `06`（例如 `hls06-passwd`），程式以此比對各台密碼。若 HLS06 再安裝一個 VCK5K 卡，則 `U50Alias = ['', '', '', '', 'vck5k_01', 'vck5k_02']`。新伺服器應設置為靜態 IP，router 裡也要確認已連上線。

**(4) 外網 IP 切換**

當預設外網故障時（如 router 切換到備用外網），使用者入口 IP 會改為 `ExternalIPBak` 設定值。此時管理者也需要執行 `python3 active_monitord.py fpga_init` 重設 monitord 的外網 IP。

> 只有一組外網時填 `ExternalIP` / `ExternalIPGateway` 即可，`ExternalIPBak` / `ExternalIPBakGateway` 保留佔位符，`monitord.py` 的 `find_external_ip()` 會固定回傳 `ExternalIP`。有兩組外網時，線路切換需由 router 自動 switch，monitord 以 `mtr` 看到 `ExternalIPBakGateway` 時才改用 `ExternalIPBak`。

```python
ExternalIP = '140.112.207.100'       # 主要外網
ExternalIPBak = '<external_ip2>'     # 備援外網，沒有時保留佔位符即可
```

**(5) 內網網段**

```python
InternalSec = '192.168.1.'    # 需對應 router 裡的實際設定值
```

**(6) Email 通知設定**

系統在加入新使用者或通知排隊中使用者時，會自動寄送通知信：

```python
SmtpPort = 587
SmtpServer = 'smtp.gmail.com'
GmailSender = '<sender-email>'
GmailPasswd = '<app-password>'
```

> Gmail 自動寄信需啟用二階段認證並綁定手機號碼。異動手機號碼時需關閉並重啟二階段認證，`GmailPasswd` 也會變動。參考：https://support.google.com/accounts/answer/185833

**(7) 排程間隔**

```python
CheckSeconds = 30     # 定期檢查設備及使用者事件的間隔（秒）
RetryMinutes = 30     # 定期重試 unknown 狀態設備的間隔（分鐘）
```

**(8) U50 專案帳號路徑**

```python
U50UserHome = '/mnt/HLSNAS/'    # 預設的 U50 專案帳號建立路徑
```

> 需要在 HLS01 ~ HLS05 伺服器及管理伺服器 HLS00 上，建立 `/mnt/HLSNAS/` 目錄並掛載到 NAS 儲存目錄（例如 `/volume2/LabData`，見 3-1-3 c），並設定 NAS 目錄可被共用的權限，用來儲存 Vitis/Vivado 專案的 GB 資料。

**完整 config.py 參數參考：**

<details>
<summary>點擊展開完整 config.py</summary>

```python
#######################################################################
# mongodb
#######################################################################
MongoIP = '172.17.0.2'
MongoPort = 27017

#######################################################################
# monitord
#######################################################################
MonitordIP = '192.168.1.10'
MonitordPort = 5000
RentedPynqMinutes = 60
RentedKv260Minutes = 120
RentedVitisMinutes = 60
RentedU50Minutes = 120
RentedU50JobMinutes = 100
RentedU50BatchHours = 6
RentedVCK5KMinutes = 240
PasswdLength = 6

PynqZ2List = ['01', '02', '03', '04', '05', '06', '07', '09', '10', '11', '12']
Kv260List = ['02', '03', '04', '05', '06', '08', '09', '10', '11', '12', '13', '20']

PynqUserName = 'xilinx'
PynqUserPasswd = 'xilinx'
PynqZ2Home = '/home/xilinx/'
Kv260UserName = 'ubuntu'
Kv260UserPasswd = 'boledukv260'
Kv260Home = '/home/ubuntu/'
PynqPython3 = '/usr/local/share/pynq-venv/bin/python3'
PynqResetFile = 'reset_pynq.py'

U50List = ['01', '02', '03', '04', '05']
U50UserNameList = ['hls01', 'hls02', 'hls03', 'hls04', 'hls05']
U50UserPassWordList = ['hls01-passwd', 'hls02-passwd', 'hls03-passwd',
                       'hls04-passwd', 'hls05-passwd']
U50BoardAvailable = [1, 1, 1, 1, 1]
U50Alias = ['', '', '', '', 'vck5k_01']
U50UserLimit = 1
U50BatchLimit = 1
U50Python3 = '/usr/bin/python3'
U50ManageUserHome = '/opt/labManageKit/'
U50ManageUserFile = 'manage_user.py'
U50JobGrabberFile = 'job_grabber.py'
U50DevGroup = 'render'
U50DockerGroup = 'docker'
U50RentedLogFile = '/opt/labManageKit/u50_rented.log'

NcCommand = 'nc -w 5'
ExternalIP = '140.112.207.100'
ExternalIPGateway = '140.112.207.254'
ExternalIPBak = '<external_ip2>'
ExternalIPBakGateway = '<external_gateway2>'
InternalSec = '192.168.1.'
DefaultSSHPort = 22
MonitordInLab = True
U50QueueEnable = True
U50QueueTimeOut = 10

#######################################################################
# onlinefpga
#######################################################################
MonitordRentRequest = 'http://' + MonitordIP + ':' + str(MonitordPort) + '/fpga_rent'
MonitordReturnRequest = 'http://' + MonitordIP + ':' + str(MonitordPort) + '/fpga_return'
VaildCodeLength = 6
SmtpPort = 587
SmtpServer = 'smtp.gmail.com'
GmailSender = '<sender-email>'
GmailPasswd = '<app-password>'
ServiceStop = '06:00'
ServiceStart = '07:00'
FindPTSCommand = "ps -ef | grep -E 'ssh.*pts' | grep -v grep | awk -F\" \" '{print $2}'"
OnlineFPGAUserManual = '<google_drive_file_url>'

#######################################################################
# manage_user
#######################################################################
U50UserHome = '/mnt/HLSNAS/'
TimeCheckFile = './.timeup_check.py'
TimeCheckPycFile = './.timeup_check.pyc'
ChangeDirFile = './.changedir.py'
ChangeDirPycFile = './.changedir.pyc'

#######################################################################
# manage_dbuser
#######################################################################

#######################################################################
# job_grabber
#######################################################################
MonitordJobUpdateRequest = 'http://' + MonitordIP + ':' + str(MonitordPort) + '/batch_jobber'

#######################################################################
# active_monitord
#######################################################################
CheckSeconds = 30
RetryMinutes = 30
MonitordInitRequest = 'http://' + MonitordIP + ':' + str(MonitordPort) + '/fpga_init'
MonitordRetryUnknownRequest = 'http://' + MonitordIP + ':' + str(MonitordPort) + '/retry_unknown'
MonitordRetryAvailRequest = 'http://' + MonitordIP + ':' + str(MonitordPort) + '/retry_available'
MonitordCheckRequest = 'http://' + MonitordIP + ':' + str(MonitordPort) + '/check_and_action'
```

</details>

---

### list_user.py

**Usage：**

```bash
python3 list_user.py all                    # 列出所有使用者資料
python3 list_user.py dump                   # 依序印出所有使用者的 email、名字及註冊日期
python3 list_user.py online                 # 列出目前在線使用者租用紀錄
python3 list_user.py rent_date 'keyword'    # 列出租用日期符合關鍵字的使用者，如 rent_date 07/23
python3 list_user.py monitord 'keyword'     # 列出租用紀錄符合關鍵字的使用者（email、裝置、U50 專案帳號、job）
python3 list_user.py filter 'keyword'       # 列出使用者資料或租用紀錄符合關鍵字的項目
```

> `monitord` 在租用紀錄（boledumonitord）的 email、device、ssh_passwd（U50 專案帳號，如 `01.AkkCVf`）及 job 欄位中搜尋關鍵字，不搜尋使用者名字。
>
> `filter` 依關鍵字內容決定搜尋範圍：關鍵字含 `pynq`、`vitis`、`u50` 或 `batch` 時，搜尋租用紀錄的 device 及 job 欄位（例如 `filter pynq_05`）；其他關鍵字則搜尋使用者資料（boleduuser）的 email、名字、密碼及註冊日期，例如 `python3 list_user.py filter 2023/06` 會印出所有 2023/06 註冊的使用者資料。`kv260` 設備或 U50 專案帳號不會被 `filter` 找到，請改用 `monitord`。

---

### manage_dbuser.py

**Usage：**

```bash
python3 manage_dbuser.py add registration.csv           # 由 CSV 匯入使用者並自動 email 通知
python3 manage_dbuser.py add email username password     # 手動加入使用者（username 及 password 指定 @ 可由系統自動產生）
python3 manage_dbuser.py del email                       # 刪除指定使用者
```

不會加入相同 email 的使用者帳號到資料庫。

**registration.csv 格式範例：**

```csv
user001@gmail.com
user002@gmail.com
user003@gmail.com
```

---

### start_monitord.sh

啟動 `active_monitord.py` 及 `monitord.py`。會根據目前時間自動判斷使用 `run_startup`（維護時間內）或 `run_routine`（維護時間外）：

```bash
#!/bin/bash
pushd /opt/labManageKit/
current_time=$(date +%H:%M)
if [[ "$current_time" > "06:00" ]] && [[ "$current_time" < "07:00" ]]; then
    python3 active_monitord.py run_startup &
else
    python3 active_monitord.py run_routine &
fi
python3 monitord.py
```

在 Ubuntu 桌面的 **Startup Application** 新增項目（每日啟動後自動執行）：

- **Name：** Monitord
- **Command：** `gnome-terminal -- "/opt/labManageKit/start_monitord.sh"`
<img width="1095" height="837" alt="260302-001" src="https://github.com/user-attachments/assets/2c36f6e9-b8a2-4d5b-9f51-91f506dea738" />

---

### stop_monitord.sh

關閉所有 monitord 相關程序：

```bash
#!/bin/bash
pkill -f start_monitord.sh
pkill -f monitord.py
pkill -f active_monitord.py
```

---

### sync_db.sh

手動備份 MongoDB 資料庫到備份目錄：

```bash
echo hls00-passwd | sudo -S rm -rf "/opt/labManageKit/backupdb/$(date +"%Y-%m-%d")"
echo hls00-passwd | sudo -S mkdir "/opt/labManageKit/backupdb/$(date +"%Y-%m-%d")"
echo hls00-passwd | sudo -S cp -rf /mnt/LabData/hls00/boledudb "/opt/labManageKit/backupdb/$(date +"%Y-%m-%d")"

echo "synchronize nfs boledudb to /opt/labManageKit/backupdb/$(date +"%Y-%m-%d")"
```

---

### sync_hlsclient.sh

手動同步管理伺服器 HLS00 的 `config.py`、`manage_user.py`、`job_grabber.py` 及 `u50_tenant_util.py` 到 HLS01 ~ HLS05 FPGA 伺服器：

```bash
# 範例（HLS01）：
sshpass -p "hls01-passwd" scp -P 1100 -o StrictHostKeyChecking=no ./config.py hls01@192.168.1.11:/opt/labManageKit/
sshpass -p "hls01-passwd" scp -P 1100 -o StrictHostKeyChecking=no ./manage_user.py hls01@192.168.1.11:/opt/labManageKit/
sshpass -p "hls01-passwd" scp -P 1100 -o StrictHostKeyChecking=no ./job_grabber.py hls01@192.168.1.11:/opt/labManageKit/
sshpass -p "hls01-passwd" scp -P 1100 -o StrictHostKeyChecking=no ./u50_tenant_util.py hls01@192.168.1.11:/opt/labManageKit/
# HLS02 ~ HLS05 以此類推...
```

> 需先安裝：`sudo apt install sshpass`

---

### u50_rented.log

HLS01 ~ HLS05 FPGA 伺服器租用紀錄檔案範例：

```
2023/05/01 18:30:07 user01@example.com returned vck5k_01
2023/05/01 19:23:15 user01@example.com rented vck5k_01
2023/05/01 19:27:07 user02@example.com returned u50_04
2023/05/01 20:12:07 user03@example.com returned u50_02
...
```

---

### u50_tenant_util.py

**Usage：**

```bash
python3 u50_tenant_util.py list              # 查詢 HLS01~HLS05 上的 U50 專案帳號
python3 u50_tenant_util.py checkdb           # 檢查是否有不一致的 U50 綁定紀錄
python3 u50_tenant_util.py del all           # 在各 FPGA 伺服器上刪除所有 U50 專案帳號及對應目錄
python3 u50_tenant_util.py del <account>     # 在各 FPGA 伺服器上刪除指定 U50 專案帳號及對應目錄
python3 u50_tenant_util.py deldb all         # 在管理伺服器上刪除所有使用者 U50 綁定紀錄
python3 u50_tenant_util.py deldb <account>   # 在管理伺服器上刪除指定使用者 U50 綁定紀錄
```

**典型使用情境：** 學期結束或專案結束時，管理者需清理 FPGA 伺服器上的專案空間：

1. 在各 FPGA 伺服器上執行 `python3 u50_tenant_util.py del all` 刪除專案帳號及對應目錄
2. 在管理伺服器上執行 `python3 u50_tenant_util.py deldb all` 刪除 U50 綁定紀錄

> **注意：** 刪除所有專案帳號時，若專案檔案數多會需較多時間，請不要中斷執行。完成後可透過 `grep 03. /etc/passwd` 確認帳號是否已移除。

> **換伺服器：** 當使用者因綁定的 HLS 伺服器租戶過多想換到其它伺服器時，可請使用者先備份對應目錄資料，管理者再移除其 U50 專案帳號、對應目錄及綁定紀錄，使用者就可以重新綁定。

**查詢範例：**

```bash
$ python3 u50_tenant_util.py list
Tenants on HLS01:
01.AkkCVf change: 2023-05-31
01.bGDTSb change: 2023-07-17
...
Total tenants: 10
Tenants on HLS02:
02.CtINEm change: 2023-06-30
...
Total tenants: 7
```

---

### utility/cleandb.sh

自動清理 /mnt/LabData/hls00/backupdb/ 中較舊的備份目錄，只保留名稱為日期的最新 27 個，避免備份佔滿 NAS 空間。腳本中 KEEP_BACKUPS=28，實際保留數為 KEEP_BACKUPS-1，即 27 個。

```bash
#!/bin/bash
KEEP_BACKUPS=28

BACKUP_DIRS=(
    "/opt/labManageKit/backupdb"
)

for BACKUP_PATH in "${BACKUP_DIRS[@]}"; do
    if [ -d "$BACKUP_PATH" ]; then
        cd "$BACKUP_PATH" || exit 1
        dirs=$(ls -1d [0-9]* | sort | head -n -$((KEEP_BACKUPS - 1)))
        if [ -n "$dirs" ]; then
            for dir in $dirs; do
                echo "Deleting $BACKUP_PATH/$dir"
                echo hls00-passwd | sudo -S rm -rf "$dir"
            done
        else
            echo "No backups to delete in $BACKUP_PATH"
        fi
    else
        echo "Directory $BACKUP_PATH not found, skipping..."
    fi
done
```

使用情境：備份目錄數量過多、磁碟空間不足時，在管理伺服器 HLS00 手動執行：

```bash
hls00@HLS00:/opt/labManageKit/utility$ ./cleandb.sh
```

有超過保留數的舊備份時，每刪除一個目錄會印出 Deleting 路徑/日期目錄；沒有需要刪除的備份時印出 No backups to delete in 路徑；備份路徑不存在時印出 Directory 路徑 not found, skipping...。清理後只剩最新 27 個日期目錄，例如 2026-10-26 查詢 backupdb/ 的結果：

```bash
hls00@HLS00:/opt/labManageKit/backupdb$ ls
2026-09-30  2026-10-03  2026-10-06  2026-10-09  2026-10-12  2026-10-15  2026-10-18  2026-10-21  2026-10-24
2026-10-01  2026-10-04  2026-10-07  2026-10-10  2026-10-13  2026-10-16  2026-10-19  2026-10-22  2026-10-25
2026-10-02  2026-10-05  2026-10-08  2026-10-11  2026-10-14  2026-10-17  2026-10-20  2026-10-23  2026-10-26
```

> [註]
> (1) 腳本中的 sudo 密碼 hls00-passwd 需改為 HLS00 實際的 sudo 密碼。
> (2) BACKUP_DIRS 需與 start_docker_boledudb.sh / sync_db.sh 實際寫入的備份目錄一致，可用 ls -ld /opt/labManageKit/backupdb 確認 /opt/labManageKit/backupdb 是否指向 /mnt/LabData/hls00/backupdb。
> (3) 只會刪除名稱以數字開頭的目錄，其他名稱的目錄 (例如修復資料庫前手動保留的 before_repair) 不會被清理，需手動移除。
> (4) 每日 06:20 自動執行，早於 06:25 的管理伺服器重啟，在 hls00 使用者的 crontab (crontab -e，不加 sudo) 設定如下：

```
# m h  dom mon dow   command
20 6 * * * /opt/labManageKit/utility/cleandb.sh
25 6 * * * echo hls00-passwd | sudo -S reboot
```

---

### utility/check_ssh_connection.sh

查詢最近的 SSH 連線詳細資料，用於檢查是否有異常 SSH 連線行為：

```bash
$ ./check_ssh_connection.sh
Jul 23 12:48:08 HLS00 sshd[8274]: pam_unix(sshd:session): session opened for user boleduuser by (uid=0)
Jul 23 12:48:35 HLS00 sshd[8501]: pam_unix(sshd:session): session opened for user hls00 by (uid=0)
...
```

---

### utility/list_subdir_size.sh

查詢特定目錄下所有子目錄的使用空間，用於檢查是否有異常的資料庫備份：

```bash
$ ./list_subdir_size.sh
Input parent dir of subdirs to calculate size :
/mnt/LabData/hls00/backupdb
502M /mnt/LabData/hls00/backupdb/2023-07-23
506M /mnt/LabData/hls00/backupdb/2023-07-21
...
3.5G /mnt/LabData/hls00/backupdb
```

---

## License

Copyright © Boledu Foundation. All rights reserved.
