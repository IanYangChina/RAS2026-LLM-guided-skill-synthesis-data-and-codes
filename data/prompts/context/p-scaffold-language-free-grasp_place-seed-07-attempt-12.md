## Search State

- **Seed**: 7
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0310 | 0.31 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1118 | 0.32 | ✅ accepted |
| 10 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ❌ rejected |
| 9 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2195 | 0.24 | ❌ rejected |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.031) — your mutation base

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

- **Composite score**: 0.031
- **task_score** (E): 0.315
- **fitness_score**: 0.631  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1691 |
| descend_1 | 1.00 | 1.00 | 0.0956 |
| grasp_1 | 1.00 | 1.00 | 0.0129 |
| lift_1 | 1.00 | 1.00 | 0.1708 |
| transport_1 | 1.00 | 1.00 | 0.2203 |
| descend_to_goal | 1.00 | 0.67 | 0.0904 |
| release_gripper | 1.00 | 1.00 | 0.0196 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.037, 0.140) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.507, 0.037, 0.140)→(0.506, 0.025, 0.045) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.025, 0.045)→(0.497, 0.025, 0.035) | (0.511, 0.022, 0.026)→(0.511, 0.024, 0.025) | 0.273→0.272 | 1.00 / 42.000 | 0.183 | 0.245 |
| lift_1 | lift | 1.00 / step_budget | (0.497, 0.025, 0.035)→(0.506, 0.024, 0.206) | (0.511, 0.024, 0.025)→(0.516, 0.024, 0.191) | 0.272→0.213 | 1.00 / 37.667 | 0.079 | 0.486 |
| transport_1 | approach | 1.00 / step_budget | (0.506, 0.024, 0.206)→(0.597, 0.195, 0.302) | (0.516, 0.024, 0.191)→(0.606, 0.195, 0.280) | 0.213→0.087 | 1.00 / 22.667 | 0.117 | 0.179 |
| descend_to_goal | descend | 1.00 / step_budget | (0.597, 0.195, 0.302)→(0.602, 0.205, 0.213) | (0.606, 0.195, 0.280)→(0.611, 0.203, 0.176) | 0.087→0.020 | 0.67 / 13.667 | 3253.468 | 0.446 |
| release_gripper | release | 1.00 / step_budget | (0.602, 0.205, 0.213)→(0.596, 0.203, 0.231) | (0.611, 0.203, 0.176)→(0.612, 0.206, 0.017) | 0.020→0.178 | 1.00 / 3.333 | 0.138 | 1.858 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.426
- phase_score: 0.633
- phase_breakdown.place_release_score: 0.458
- phase_breakdown.grasp_contact_score: 0.744
- phase_breakdown.pre_grasp_score: 0.672
- phase_breakdown.lift_clearance_score: 0.615
- phase_breakdown.transport_to_goal_score: 0.675
- grasp_place_fitness: 0.686

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.686
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.426
- **Median Q (composite search score)**: 0.013
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.285


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.78864,"average_solve_count":440.0,"average_success_count":440.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.05602,"approach_1.speed":0.09362,"descend_1.speed":0.04836,"descend_to_goal.speed":0.01332,"grasp_1.max_time":1.63198,"lift_1.speed":0.03471,"release_gripper.max_time":0.67823,"transport_1.arc_height":0.11478,"transport_1.speed":0.0298},"optimized_scores":{"best_composite_score":0.08632,"best_fitness_score":0.68632,"best_task_score":0.42585},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":121.0,"contact_point_centroid":[0.62724,0.16214,-0.00911],"force_p95":1.47109,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.56768,"mean_force":0.62161,"phase_index":6.0,"phase_name":"release_gripper","phase_type":"release","tcp_position_centroid":[0.61485,0.16668,0.17216]},{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.50885,0.04166,-0.00161],"force_p95":0.43795,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46173,"mean_force":0.18171,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49784,0.04132,0.03642]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2281.0,"contact_point_centroid":[0.62045,0.14542,0.21304],"force_p95":0.11245,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37214,"mean_force":0.07583,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61716,0.16416,0.21248]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":910.0,"contact_point_centroid":[0.62356,0.18668,0.15819],"force_p95":0.11388,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33488,"mean_force":0.06692,"phase_index":6.0,"phase_name":"release_gripper","phase_type":"release","tcp_position_centroid":[0.61878,0.168,0.15755]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2551.0,"contact_point_centroid":[0.62168,0.18287,0.21308],"force_p95":0.09502,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32947,"mean_force":0.06965,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61716,0.16417,0.21233]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":877.0,"contact_point_centroid":[0.62217,0.14901,0.15769],"force_p95":0.13922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32229,"mean_force":0.07328,"phase_index":6.0,"phase_name":"release_gripper","phase_type":"release","tcp_position_centroid":[0.61861,0.16795,0.15727]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11693.0,"contact_point_centroid":[0.50167,0.06017,0.12008],"force_p95":0.07964,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26909,"mean_force":0.05466,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50145,0.041,0.11765]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12408.0,"contact_point_centroid":[0.50156,0.02193,0.11892],"force_p95":0.07711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2472,"mean_force":0.05225,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50138,0.04101,0.11671]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03996,-0.00216],"force_p95":0.16732,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23799,"mean_force":0.1344,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50002,0.04152,0.03673]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4069.0,"contact_point_centroid":[0.49958,0.06065,0.03814],"force_p95":0.08092,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15228,"mean_force":0.05195,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49887,0.04143,0.03548]},{"body_a":"world","body_b":"grasp_target","contact_count":1520.0,"contact_point_centroid":[0.51251,0.03972,-0.00191],"force_p95":0.1347,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50237,0.05148,0.23239]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50659,0.04801,0.09519]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11213.0,"contact_point_centroid":[0.54739,0.10379,0.26544],"force_p95":0.08633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11365,"mean_force":0.05945,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54603,0.08467,0.2634]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12956.0,"contact_point_centroid":[0.54507,0.06337,0.26411],"force_p95":0.07807,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10615,"mean_force":0.05244,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54387,0.08229,0.26261]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5028.0,"contact_point_centroid":[0.49959,0.02227,0.03741],"force_p95":0.07315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08027,"mean_force":0.0444,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49887,0.04143,0.03549]}],"total_contact_groups":15},"final_pose_error":0.01952,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.63199,0.16448,0.0173],"final_tcp_position":[0.62123,0.16861,0.16307],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.56768,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1520.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.50763,0.05373,0.14317],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11809,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":200.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":800.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.50739,0.04226,0.04507],"tcp_start":[0.50763,0.05373,0.14317],"tcp_to_object_dist_end":0.01988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51244,0.04121,0.02547],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21164,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15951,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10897.0,"raw_peak_contact_force":0.23799,"subtask_id":"grasp_contact","tcp_end":[0.49884,0.04143,0.03545],"tcp_start":[0.50739,0.04226,0.04507],"tcp_to_object_dist_end":0.01687,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":618.0,"n_steps_budget":1000.0,"object_pos_end":[0.51775,0.04078,0.19155],"object_pos_start":[0.51244,0.04121,0.02547],"object_to_goal_dist_end":0.17771,"object_to_goal_dist_start":0.21164,"object_z_max":0.19129,"peak_contact_force":0.07966,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24197.0,"raw_peak_contact_force":0.46173,"subtask_id":"lift_clearance","tcp_end":[0.50821,0.04093,0.20609],"tcp_start":[0.49884,0.04143,0.03545],"tcp_to_object_dist_end":0.01739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":681.0,"n_steps_budget":1000.0,"object_pos_end":[0.62448,0.16063,0.23569],"object_pos_start":[0.51775,0.04078,0.19155],"object_to_goal_dist_end":0.0915,"object_to_goal_dist_start":0.17771,"object_z_max":0.27196,"peak_contact_force":0.08671,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24169.0,"raw_peak_contact_force":0.11365,"subtask_id":"transport_to_goal","tcp_end":[0.61543,0.16089,0.25522],"tcp_start":[0.50821,0.04093,0.20609],"tcp_to_object_dist_end":0.02152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":182.0,"n_steps_budget":1000.0,"object_pos_end":[0.63139,0.16835,0.14191],"object_pos_start":[0.62448,0.16063,0.23569],"object_to_goal_dist_end":0.00646,"object_to_goal_dist_start":0.0915,"object_z_max":0.23569,"peak_contact_force":0.09832,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4832.0,"raw_peak_contact_force":0.37214,"subtask_id":"place_release","tcp_end":[0.62123,0.16861,0.16307],"tcp_start":[0.61543,0.16089,0.25522],"tcp_to_object_dist_end":0.02348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63199,0.16448,0.0173],"object_pos_start":[0.63139,0.16835,0.14191],"object_to_goal_dist_end":0.12805,"object_to_goal_dist_start":0.00646,"object_z_max":0.14191,"peak_contact_force":0.17433,"phase_name":"release_gripper","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1908.0,"raw_peak_contact_force":1.56768,"subtask_id":"place_release","tcp_end":[0.61479,0.16666,0.18146],"tcp_start":[0.62123,0.16861,0.16307],"tcp_to_object_dist_end":0.16507,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96186,"average_solve_count":472.0,"average_success_count":472.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.04753,"approach_1.speed":0.02319,"descend_1.speed":0.05329,"descend_to_goal.speed":0.02451,"grasp_1.max_time":1.31149,"lift_1.speed":0.04094,"release_gripper.max_time":0.54946,"transport_1.arc_height":0.12925,"transport_1.speed":0.024},"optimized_scores":{"best_composite_score":-0.0058,"best_fitness_score":0.5942,"best_task_score":0.24037},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":336.0,"contact_point_centroid":[0.58289,0.23258,-0.00583],"force_p95":1.05822,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.09112,"mean_force":0.27145,"phase_index":6.0,"phase_name":"release_gripper","phase_type":"release","tcp_position_centroid":[0.57317,0.22219,0.25623]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.47905,0.04942,-0.00148],"force_p95":0.45752,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47912,"mean_force":0.18952,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46954,0.04948,0.03783]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1480.0,"contact_point_centroid":[0.57954,0.23659,0.29394],"force_p95":0.13993,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43862,"mean_force":0.10956,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57418,0.21832,0.298]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1471.0,"contact_point_centroid":[0.57967,0.20019,0.29444],"force_p95":0.14416,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42557,"mean_force":0.10817,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57418,0.21832,0.29796]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.5826,0.20593,0.24041],"force_p95":0.3288,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3937,"mean_force":0.20788,"phase_index":6.0,"phase_name":"release_gripper","phase_type":"release","tcp_position_centroid":[0.57657,0.22396,0.24614]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11521.0,"contact_point_centroid":[0.47277,0.06832,0.12137],"force_p95":0.07485,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27273,"mean_force":0.05301,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4726,0.04915,0.11938]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11910.0,"contact_point_centroid":[0.47286,0.03003,0.12366],"force_p95":0.07475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24128,"mean_force":0.0515,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47275,0.04915,0.1216]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":209.0,"contact_point_centroid":[0.58177,0.24081,0.23995],"force_p95":0.17298,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23943,"mean_force":0.09377,"phase_index":6.0,"phase_name":"release_gripper","phase_type":"release","tcp_position_centroid":[0.57633,0.22385,0.24552]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48271,0.04883,-0.00208],"force_p95":0.14535,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19698,"mean_force":0.12872,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47155,0.0497,0.03793]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15435.0,"contact_point_centroid":[0.49888,0.06346,0.31212],"force_p95":0.09735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17896,"mean_force":0.06358,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49589,0.08218,0.31091]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14317.0,"contact_point_centroid":[0.49876,0.10115,0.31102],"force_p95":0.10518,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16802,"mean_force":0.06796,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49592,0.08222,0.30957]},{"body_a":"world","body_b":"grasp_target","contact_count":1532.0,"contact_point_centroid":[0.4827,0.04873,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49132,0.04913,0.23429]},{"body_a":"world","body_b":"grasp_target","contact_count":828.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47925,0.05504,0.09682]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5061.0,"contact_point_centroid":[0.47019,0.06886,0.03944],"force_p95":0.06615,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10082,"mean_force":0.04303,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47045,0.04959,0.03682]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5427.0,"contact_point_centroid":[0.47006,0.03034,0.03914],"force_p95":0.06515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07323,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47046,0.04959,0.03682]}],"total_contact_groups":15},"final_pose_error":0.01953,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58267,0.23254,0.01668],"final_tcp_position":[0.57741,0.22413,0.2489],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":384.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1532.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.48152,0.05962,0.14633],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":828.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.47857,0.05049,0.0454],"tcp_start":[0.48152,0.05962,0.14633],"tcp_to_object_dist_end":0.01989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04942,0.02572],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28979,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.14279,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12288.0,"raw_peak_contact_force":0.19698,"subtask_id":"grasp_contact","tcp_end":[0.47042,0.04959,0.03679],"tcp_start":[0.47857,0.05049,0.0454],"tcp_to_object_dist_end":0.01646,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":586.0,"n_steps_budget":1000.0,"object_pos_end":[0.48735,0.04917,0.1914],"object_pos_start":[0.48261,0.04942,0.02572],"object_to_goal_dist_end":0.20675,"object_to_goal_dist_start":0.28979,"object_z_max":0.19112,"peak_contact_force":0.07829,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23517.0,"raw_peak_contact_force":0.47912,"subtask_id":"lift_clearance","tcp_end":[0.47853,0.0491,0.20628],"tcp_start":[0.47042,0.04959,0.03679],"tcp_to_object_dist_end":0.0173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.58238,0.21376,0.31557],"object_pos_start":[0.48735,0.04917,0.1914],"object_to_goal_dist_end":0.08641,"object_to_goal_dist_start":0.20675,"object_z_max":0.35356,"peak_contact_force":0.11403,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29752.0,"raw_peak_contact_force":0.17896,"subtask_id":"transport_to_goal","tcp_end":[0.57248,0.21394,0.33916],"tcp_start":[0.47853,0.0491,0.20628],"tcp_to_object_dist_end":0.02559,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":13.0,"n_steps":175.0,"n_steps_budget":1000.0,"object_pos_end":[0.58436,0.22393,0.22203],"object_pos_start":[0.58238,0.21376,0.31557],"object_to_goal_dist_end":0.0101,"object_to_goal_dist_start":0.08641,"object_z_max":0.31557,"peak_contact_force":9760.30694,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2951.0,"raw_peak_contact_force":0.43862,"subtask_id":"place_release","tcp_end":[0.57741,0.22413,0.2489],"tcp_start":[0.57248,0.21394,0.33916],"tcp_to_object_dist_end":0.02775,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58267,0.23254,0.01668],"object_pos_start":[0.58436,0.22393,0.22203],"object_to_goal_dist_end":0.21384,"object_to_goal_dist_start":0.0101,"object_z_max":0.22203,"peak_contact_force":0.1172,"phase_name":"release_gripper","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":638.0,"raw_peak_contact_force":2.09112,"subtask_id":"place_release","tcp_end":[0.57313,0.22216,0.26848],"tcp_start":[0.57741,0.22413,0.2489],"tcp_to_object_dist_end":0.25219,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17225,"average_solve_count":418.0,"average_success_count":418.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.07262,"approach_1.speed":0.04646,"descend_1.speed":0.07115,"descend_to_goal.speed":0.0279,"grasp_1.max_time":1.23352,"lift_1.speed":0.0218,"release_gripper.max_time":0.75402,"transport_1.arc_height":0.09036,"transport_1.speed":0.05021},"optimized_scores":{"best_composite_score":0.01253,"best_fitness_score":0.61253,"best_task_score":0.27835},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":605.0,"contact_point_centroid":[0.62084,0.22101,-0.00409],"force_p95":0.85757,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.91435,"mean_force":0.20992,"phase_index":6.0,"phase_name":"release_gripper","phase_type":"release","tcp_position_centroid":[0.60179,0.22033,0.22581]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":901.0,"contact_point_centroid":[0.60916,0.23181,0.28005],"force_p95":0.19761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52758,"mean_force":0.12716,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60363,0.21365,0.2841]},{"body_a":"world","body_b":"grasp_target","contact_count":112.0,"contact_point_centroid":[0.53314,-0.01645,-0.00182],"force_p95":0.44022,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51708,"mean_force":0.17511,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52161,-0.01688,0.03517]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1111.0,"contact_point_centroid":[0.60914,0.19651,0.27622],"force_p95":0.14357,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44858,"mean_force":0.1042,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60377,0.21417,0.28043]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53722,-0.02072,-0.00237],"force_p95":0.27192,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30108,"mean_force":0.17957,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52401,-0.01691,0.03526]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10946.0,"contact_point_centroid":[0.52669,0.00203,0.1212],"force_p95":0.08856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28562,"mean_force":0.06029,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52571,-0.01716,0.1183]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13138.0,"contact_point_centroid":[0.52604,-0.03615,0.11942],"force_p95":0.08029,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27728,"mean_force":0.05269,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52562,-0.01715,0.1174]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13834.0,"contact_point_centroid":[0.55776,0.03766,0.29642],"force_p95":0.10067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24568,"mean_force":0.06917,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55411,0.05631,0.2956]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12981.0,"contact_point_centroid":[0.55598,0.07029,0.29246],"force_p95":0.1096,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23456,"mean_force":0.07257,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55256,0.05152,0.29145]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3364.0,"contact_point_centroid":[0.52507,0.00238,0.03755],"force_p95":0.10855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21194,"mean_force":0.07238,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52281,-0.01689,0.03389]},{"body_a":"world","body_b":"grasp_target","contact_count":1888.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51502,0.03605,0.21358]},{"body_a":"world","body_b":"grasp_target","contact_count":676.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53101,-0.00943,0.08831]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4986.0,"contact_point_centroid":[0.52394,-0.0363,0.03573],"force_p95":0.08913,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10677,"mean_force":0.0547,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52283,-0.01689,0.03391]}],"total_contact_groups":13},"final_pose_error":0.01958,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.62089,0.22085,0.016],"final_tcp_position":[0.60611,0.22209,0.22568],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.91435,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":473.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1888.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53169,-0.00226,0.12979],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10565,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":169.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":676.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.53169,-0.01686,0.04436],"tcp_start":[0.53169,-0.00226,0.12979],"tcp_to_object_dist_end":0.01961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53704,-0.01759,0.02479],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31451,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.24642,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10150.0,"raw_peak_contact_force":0.30108,"subtask_id":"grasp_contact","tcp_end":[0.52278,-0.01689,0.03386],"tcp_start":[0.53169,-0.01686,0.04436],"tcp_to_object_dist_end":0.01691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":649.0,"n_steps_budget":1000.0,"object_pos_end":[0.54254,-0.0177,0.19111],"object_pos_start":[0.53704,-0.01759,0.02479],"object_to_goal_dist_end":0.25516,"object_to_goal_dist_start":0.31451,"object_z_max":0.19085,"peak_contact_force":0.0791,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24196.0,"raw_peak_contact_force":0.51708,"subtask_id":"lift_clearance","tcp_end":[0.5327,-0.01749,0.20539],"tcp_start":[0.52278,-0.01689,0.03386],"tcp_to_object_dist_end":0.01735,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":973.0,"n_steps_budget":1000.0,"object_pos_end":[0.61183,0.21015,0.28831],"object_pos_start":[0.54254,-0.0177,0.19111],"object_to_goal_dist_end":0.0828,"object_to_goal_dist_start":0.25516,"object_z_max":0.32153,"peak_contact_force":0.15114,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26815.0,"raw_peak_contact_force":0.24568,"subtask_id":"transport_to_goal","tcp_end":[0.60343,0.21001,0.31224],"tcp_start":[0.5327,-0.01749,0.20539],"tcp_to_object_dist_end":0.02536,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":165.0,"n_steps_budget":1000.0,"object_pos_end":[0.6165,0.21591,0.16475],"object_pos_start":[0.61183,0.21015,0.28831],"object_to_goal_dist_end":0.0447,"object_to_goal_dist_start":0.0828,"object_z_max":0.28831,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2012.0,"raw_peak_contact_force":0.52758,"subtask_id":"place_release","tcp_end":[0.60611,0.22209,0.22568],"tcp_start":[0.60343,0.21001,0.31224],"tcp_to_object_dist_end":0.06211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62089,0.22085,0.016],"object_pos_start":[0.6165,0.21591,0.16475],"object_to_goal_dist_end":0.19183,"object_to_goal_dist_start":0.0447,"object_z_max":0.16475,"peak_contact_force":0.12312,"phase_name":"release_gripper","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":605.0,"raw_peak_contact_force":1.91435,"subtask_id":"place_release","tcp_end":[0.6013,0.22007,0.2441],"tcp_start":[0.60611,0.22209,0.22568],"tcp_to_object_dist_end":0.22895,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```