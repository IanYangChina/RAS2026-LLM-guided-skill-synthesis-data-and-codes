## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1118 | 0.32 | ✅ accepted |
| 10 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ❌ rejected |
| 9 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2195 | 0.24 | ❌ rejected |
| 7 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ❌ rejected |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: grasp_place
- Frozen realised-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`
- Frozen object start: [0.5125095466604667, 0.039721380096957554, 0.03]
- Frozen task target: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Goal object position: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5125095466604667, 0.039721380096957554, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.5125095466604667, 0.039721380096957554, 0.03]}
  frozen_targets: {'place_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5125095466604667, 0.039721380096957554, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6275685690245193, 0.17252071899905919, 0.14502494273668382) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.112) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_contact
  anchor: object
  weight: 0.2
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: transport_to_goal
  weight: 0.2
- id: place_release
  weight: 0.2
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_grasp
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_contact
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    max_time:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: grasp_contact
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_clearance
- id: transport_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_to_goal
- id: release_1
  type: release
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_release

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.112
- **task_score** (E): 0.316
- **fitness_score**: 0.632  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1710 |
| descend_1 | 1.00 | 1.00 | 0.0942 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.1212 |
| transport_1 | 1.00 | 1.00 | 0.2045 |
| release_1 | 1.00 | 1.00 | 0.0211 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.038, 0.138) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.507, 0.038, 0.138)→(0.506, 0.026, 0.045) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 12.017 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.026, 0.045)→(0.497, 0.025, 0.035) | (0.511, 0.022, 0.026)→(0.511, 0.025, 0.025) | 0.273→0.272 | 1.00 / 42.000 | 0.186 | 0.250 |
| lift_1 | lift | 1.00 / step_budget | (0.497, 0.025, 0.035)→(0.506, 0.024, 0.156) | (0.511, 0.025, 0.025)→(0.519, 0.024, 0.142) | 0.272→0.217 | 1.00 / 28.667 | 0.097 | 0.525 |
| transport_1 | approach | 1.00 / step_budget | (0.506, 0.024, 0.156)→(0.597, 0.196, 0.202) | (0.519, 0.024, 0.142)→(0.604, 0.196, 0.108) | 0.217→0.090 | 1.00 / 12.000 | 0.121 | 0.982 |
| release_1 | release | 1.00 / step_budget | (0.597, 0.196, 0.202)→(0.594, 0.196, 0.223) | (0.604, 0.196, 0.108)→(0.609, 0.203, 0.017) | 0.090→0.178 | 1.00 / 3.333 | 0.120 | 1.163 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.432
- phase_score: 0.638
- phase_breakdown.place_release_score: 0.483
- phase_breakdown.grasp_contact_score: 0.743
- phase_breakdown.pre_grasp_score: 0.675
- phase_breakdown.lift_clearance_score: 0.614
- phase_breakdown.transport_to_goal_score: 0.676
- grasp_place_fitness: 0.689

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.689
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.432
- **Median Q (composite search score)**: 0.093
- **K-run variance**: 0.0017
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.276


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16783,"average_solve_count":286.0,"average_success_count":286.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.06766,"approach_1.speed":0.06865,"descend_1.speed":0.05091,"grasp_1.max_time":0.95665,"lift_1.speed":0.06318,"release_1.speed":0.03237,"transport_1.arc_height":0.06027,"transport_1.speed":0.01651},"optimized_scores":{"best_composite_score":0.16924,"best_fitness_score":0.68924,"best_task_score":0.43169},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":131.0,"contact_point_centroid":[0.62652,0.16547,-0.0092],"force_p95":1.48938,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51389,"mean_force":0.54718,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61259,0.1628,0.16684]},{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.50998,0.04246,-0.00152],"force_p95":0.44797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51236,"mean_force":0.11583,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49786,0.04183,0.03678]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":281.0,"contact_point_centroid":[0.62059,0.14541,0.14928],"force_p95":0.19102,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49139,"mean_force":0.10354,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61526,0.16329,0.15277]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":330.0,"contact_point_centroid":[0.62017,0.18226,0.14754],"force_p95":0.18549,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4723,"mean_force":0.09242,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61507,0.16339,0.15186]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6676.0,"contact_point_centroid":[0.50281,0.06056,0.09251],"force_p95":0.10719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30315,"mean_force":0.06677,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50086,0.04147,0.09031]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7585.0,"contact_point_centroid":[0.50268,0.02264,0.09107],"force_p95":0.10024,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27941,"mean_force":0.06056,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5008,0.04147,0.08945]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51259,0.04004,-0.0022],"force_p95":0.18032,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25035,"mean_force":0.1376,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50003,0.04205,0.03659]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6078.0,"contact_point_centroid":[0.55738,0.1112,0.18821],"force_p95":0.13343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1944,"mean_force":0.09219,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55191,0.09257,0.18707]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6995.0,"contact_point_centroid":[0.55742,0.07413,0.18771],"force_p95":0.11566,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19195,"mean_force":0.08171,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55182,0.09249,0.18677]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3777.0,"contact_point_centroid":[0.50012,0.06117,0.0382],"force_p95":0.08598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15634,"mean_force":0.05555,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49888,0.04195,0.03534]},{"body_a":"world","body_b":"grasp_target","contact_count":1704.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5022,0.05865,0.23339]},{"body_a":"world","body_b":"grasp_target","contact_count":780.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50668,0.04948,0.09357]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5010.0,"contact_point_centroid":[0.4997,0.0228,0.0373],"force_p95":0.07651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08121,"mean_force":0.04486,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49889,0.04195,0.03535]}],"total_contact_groups":13},"final_pose_error":0.01586,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62729,0.17155,0.01902],"final_tcp_position":[0.61594,0.16383,0.15142],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.51389,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":427.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1704.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.50773,0.05602,0.13993],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11517,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":780.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.50739,0.04281,0.04491],"tcp_start":[0.50773,0.05602,0.13993],"tcp_to_object_dist_end":0.01981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51246,0.04162,0.02533],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21145,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.16875,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10587.0,"raw_peak_contact_force":0.25035,"subtask_id":"grasp_contact","tcp_end":[0.49885,0.04195,0.03531],"tcp_start":[0.50739,0.04281,0.04491],"tcp_to_object_dist_end":0.01688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":425.0,"n_steps_budget":1000.0,"object_pos_end":[0.52285,0.04128,0.14106],"object_pos_start":[0.51246,0.04162,0.02533],"object_to_goal_dist_end":0.16794,"object_to_goal_dist_start":0.21145,"object_z_max":0.1408,"peak_contact_force":0.10824,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14351.0,"raw_peak_contact_force":0.51236,"subtask_id":"lift_clearance","tcp_end":[0.50734,0.04131,0.15619],"tcp_start":[0.49885,0.04195,0.03531],"tcp_to_object_dist_end":0.02167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":601.0,"n_steps_budget":1000.0,"object_pos_end":[0.6244,0.16264,0.13316],"object_pos_start":[0.52285,0.04128,0.14106],"object_to_goal_dist_end":0.01577,"object_to_goal_dist_start":0.16794,"object_z_max":0.18271,"peak_contact_force":0.13037,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13073.0,"raw_peak_contact_force":0.1944,"subtask_id":"transport_to_goal","tcp_end":[0.61587,0.16253,0.15713],"tcp_start":[0.50734,0.04131,0.15619],"tcp_to_object_dist_end":0.02544,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.62729,0.17155,0.01902],"object_pos_start":[0.6244,0.16264,0.13316],"object_to_goal_dist_end":0.12601,"object_to_goal_dist_start":0.01577,"object_z_max":0.13316,"peak_contact_force":0.14346,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":742.0,"raw_peak_contact_force":1.51389,"subtask_id":"place_release","tcp_end":[0.61256,0.16277,0.17676],"tcp_start":[0.61587,0.16253,0.15713],"tcp_to_object_dist_end":0.15867,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30634,"average_solve_count":284.0,"average_success_count":284.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.04918,"approach_1.speed":0.06502,"descend_1.speed":0.03293,"grasp_1.max_time":0.62843,"lift_1.speed":0.03975,"release_1.speed":0.04495,"transport_1.arc_height":0.08594,"transport_1.speed":0.07421},"optimized_scores":{"best_composite_score":0.0737,"best_fitness_score":0.5937,"best_task_score":0.23878},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":157.0,"contact_point_centroid":[0.57826,0.21754,-0.00994],"force_p95":1.54836,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.55558,"mean_force":0.52699,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56824,0.20829,0.24531]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.4791,0.04986,-0.00149],"force_p95":0.46399,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48861,"mean_force":0.18736,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46954,0.0495,0.03746]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8275.0,"contact_point_centroid":[0.49848,0.10159,0.22688],"force_p95":0.12071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28686,"mean_force":0.07538,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49503,0.08278,0.22566]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8686.0,"contact_point_centroid":[0.49566,0.05959,0.22353],"force_p95":0.13827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28397,"mean_force":0.07202,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49239,0.07829,0.22238]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8395.0,"contact_point_centroid":[0.47263,0.06833,0.09703],"force_p95":0.07423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27873,"mean_force":0.05268,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47244,0.04916,0.09523]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8401.0,"contact_point_centroid":[0.47265,0.03002,0.09718],"force_p95":0.07562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24942,"mean_force":0.05255,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47244,0.04917,0.09519]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48271,0.04883,-0.00208],"force_p95":0.14618,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19913,"mean_force":0.12896,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47152,0.04973,0.03759]},{"body_a":"world","body_b":"grasp_target","contact_count":1476.0,"contact_point_centroid":[0.4827,0.04873,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49133,0.05043,0.23392]},{"body_a":"world","body_b":"grasp_target","contact_count":680.0,"contact_point_centroid":[0.57771,0.21697,-0.00216],"force_p95":0.12619,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12697,"mean_force":0.111,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57012,0.21557,0.24075]},{"body_a":"world","body_b":"grasp_target","contact_count":844.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47911,0.05522,0.09703]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5060.0,"contact_point_centroid":[0.47017,0.06888,0.03912],"force_p95":0.06629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11338,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47043,0.04962,0.03648]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5429.0,"contact_point_centroid":[0.47005,0.03037,0.03882],"force_p95":0.06528,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07185,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47043,0.04962,0.03648]},{"body_a":"left_finger","body_b":"right_finger","contact_count":84.0,"contact_point_centroid":[0.57151,0.21538,0.23757],"force_p95":0.01523,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01563,"mean_force":0.01151,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57125,0.21535,0.23569]}],"total_contact_groups":13},"final_pose_error":0.01636,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57772,0.21696,0.01602],"final_tcp_position":[0.57195,0.21637,0.23415],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":35.8048,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1476.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.48149,0.05987,0.14602],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":35.8048,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":844.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.47855,0.05052,0.04505],"tcp_start":[0.48149,0.05987,0.14602],"tcp_to_object_dist_end":0.01956,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04944,0.0257],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28979,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.14349,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12289.0,"raw_peak_contact_force":0.19913,"subtask_id":"grasp_contact","tcp_end":[0.4704,0.04961,0.03645],"tcp_start":[0.47855,0.05052,0.04505],"tcp_to_object_dist_end":0.01626,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":419.0,"n_steps_budget":1000.0,"object_pos_end":[0.48741,0.04896,0.1433],"object_pos_start":[0.48261,0.04944,0.0257],"object_to_goal_dist_end":0.2211,"object_to_goal_dist_start":0.28979,"object_z_max":0.14303,"peak_contact_force":0.07378,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16884.0,"raw_peak_contact_force":0.48861,"subtask_id":"lift_clearance","tcp_end":[0.47783,0.04909,0.1565],"tcp_start":[0.4704,0.04961,0.03645],"tcp_to_object_dist_end":0.01632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":772.0,"n_steps_budget":1000.0,"object_pos_end":[0.57848,0.21553,0.00739],"object_pos_start":[0.48741,0.04896,0.1433],"object_to_goal_dist_end":0.22352,"object_to_goal_dist_start":0.2211,"object_z_max":0.25207,"peak_contact_force":0.07973,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17118.0,"raw_peak_contact_force":2.55558,"subtask_id":"transport_to_goal","tcp_end":[0.57164,0.21429,0.23879],"tcp_start":[0.47783,0.04909,0.1565],"tcp_to_object_dist_end":0.23151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.57772,0.21696,0.01602],"object_pos_start":[0.57848,0.21553,0.00739],"object_to_goal_dist_end":0.21483,"object_to_goal_dist_start":0.22352,"object_z_max":0.01681,"peak_contact_force":0.12262,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":764.0,"raw_peak_contact_force":0.12697,"subtask_id":"place_release","tcp_end":[0.56969,0.21529,0.26009],"tcp_start":[0.57164,0.21429,0.23879],"tcp_to_object_dist_end":0.24421,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47955,"average_solve_count":269.0,"average_success_count":269.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.09843,"approach_1.speed":0.06872,"descend_1.speed":0.03124,"grasp_1.max_time":1.34337,"lift_1.speed":0.06511,"release_1.speed":0.0546,"transport_1.arc_height":0.05754,"transport_1.speed":0.0647},"optimized_scores":{"best_composite_score":0.09257,"best_fitness_score":0.61257,"best_task_score":0.27862},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":265.0,"contact_point_centroid":[0.62215,0.22174,-0.00632],"force_p95":1.15478,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.84759,"mean_force":0.30724,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59932,0.21133,0.22084]},{"body_a":"world","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.5345,-0.01587,-0.00171],"force_p95":0.48074,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57269,"mean_force":0.12746,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52163,-0.01683,0.03562]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.60775,0.2293,0.20133],"force_p95":0.26419,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47071,"mean_force":0.16476,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60155,0.21105,0.20694]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":204.0,"contact_point_centroid":[0.60684,0.19374,0.20166],"force_p95":0.18179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38802,"mean_force":0.09553,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60152,0.21127,0.2066]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6260.0,"contact_point_centroid":[0.5278,0.00191,0.09169],"force_p95":0.11393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32232,"mean_force":0.07379,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5249,-0.01708,0.08925]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7357.0,"contact_point_centroid":[0.52727,-0.03583,0.08998],"force_p95":0.10514,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31638,"mean_force":0.06606,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52484,-0.01707,0.08847]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53723,-0.02071,-0.00237],"force_p95":0.27246,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30194,"mean_force":0.17978,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52395,-0.01686,0.03527]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3358.0,"contact_point_centroid":[0.52503,0.00243,0.03757],"force_p95":0.1089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21148,"mean_force":0.07248,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52275,-0.01684,0.03391]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8343.0,"contact_point_centroid":[0.56312,0.0534,0.20813],"force_p95":0.13237,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19714,"mean_force":0.08879,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55762,0.07175,0.20815]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7653.0,"contact_point_centroid":[0.56395,0.09274,0.20893],"force_p95":0.13567,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18848,"mean_force":0.09494,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55843,0.07428,0.20897]},{"body_a":"world","body_b":"grasp_target","contact_count":1916.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13319,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51536,0.03951,0.21246]},{"body_a":"world","body_b":"grasp_target","contact_count":704.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53097,-0.00931,0.0883]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4992.0,"contact_point_centroid":[0.5239,-0.03626,0.03574],"force_p95":0.08935,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10712,"mean_force":0.05471,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52277,-0.01684,0.03393]}],"total_contact_groups":13},"final_pose_error":0.0176,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.62337,0.22191,0.01626],"final_tcp_position":[0.60194,0.21239,0.2055],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.84759,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":480.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1916.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53199,-0.00238,0.12833],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10416,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":176.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":704.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.53159,-0.01682,0.04432],"tcp_start":[0.53199,-0.00238,0.12833],"tcp_to_object_dist_end":0.01961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53704,-0.01755,0.02478],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31447,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.24694,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10150.0,"raw_peak_contact_force":0.30194,"subtask_id":"grasp_contact","tcp_end":[0.52272,-0.01684,0.03387],"tcp_start":[0.53159,-0.01682,0.04432],"tcp_to_object_dist_end":0.01697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":444.0,"n_steps_budget":1000.0,"object_pos_end":[0.54744,-0.01767,0.14061],"object_pos_start":[0.53704,-0.01755,0.02478],"object_to_goal_dist_end":0.26201,"object_to_goal_dist_start":0.31447,"object_z_max":0.14037,"peak_contact_force":0.10893,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13716.0,"raw_peak_contact_force":0.57269,"subtask_id":"lift_clearance","tcp_end":[0.53179,-0.01741,0.15574],"tcp_start":[0.52272,-0.01684,0.03387],"tcp_to_object_dist_end":0.02177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":791.0,"n_steps_budget":1000.0,"object_pos_end":[0.60822,0.20954,0.18336],"object_pos_start":[0.54744,-0.01767,0.14061],"object_to_goal_dist_end":0.03024,"object_to_goal_dist_start":0.26201,"object_z_max":0.21087,"peak_contact_force":0.15337,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15996.0,"raw_peak_contact_force":0.19714,"subtask_id":"transport_to_goal","tcp_end":[0.60209,0.20982,0.20909],"tcp_start":[0.53179,-0.01741,0.15574],"tcp_to_object_dist_end":0.02645,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.62337,0.22191,0.01626],"object_pos_start":[0.60822,0.20954,0.18336],"object_to_goal_dist_end":0.19169,"object_to_goal_dist_start":0.03024,"object_z_max":0.18336,"peak_contact_force":0.09381,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":597.0,"raw_peak_contact_force":1.84759,"subtask_id":"place_release","tcp_end":[0.59931,0.21127,0.2308],"tcp_start":[0.60209,0.20982,0.20909],"tcp_to_object_dist_end":0.21615,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```