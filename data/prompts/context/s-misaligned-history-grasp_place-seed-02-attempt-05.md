## Search State

- **Seed**: 2
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | 0.1129 | 0.89 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | impedance_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | -0.2015 | 0.37 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14  | 0.1073 | 0.16 | ❌ rejected |
| 2 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0  | 0.1073 | 0.16 | ❌ rejected |
| 1 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0  | 0.1660 | 1.00 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
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
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.4761612134249316, -0.02015088565858767, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.631422574059428, 0.1591915942135097, 0.1900150788948481) | final destination targets |
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

## Current Skill (Q=0.166) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: place_goal
  target_entity: object
  weight: 0.5
phases:
- id: approach_object
  type: approach
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
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    approach_offset_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    approach_offset_y:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    approach_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - -0.01
    orientation:
      mode: keep_current
  parameters:
    descend_grasp_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    descend_grasp_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    descend_grasp_z:
      type: scalar
      range:
      - -0.02
      - 0.0
      default: -0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: grasp_guard
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift
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
    - 0.2
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.15
      - 0.25
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_object
- id: approach_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.07
    orientation:
      mode: keep_current
  parameters:
    approach_goal_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    approach_goal_y:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    approach_goal_z:
      type: scalar
      range:
      - 0.03
      - 0.12
      default: 0.07
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    place_x:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    place_y:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    place_z:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_x: status=consumed; consumers=target.offset.x (add)
    - approach_offset_y: status=consumed; consumers=target.offset.y (add)
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, -0.01]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_grasp_x: status=consumed; consumers=target.offset.x (add)
    - descend_grasp_y: status=consumed; consumers=target.offset.y (add)
    - descend_grasp_z: status=consumed; consumers=target.offset.z (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_guard, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.07]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_x: status=consumed; consumers=target.offset.x (add)
    - approach_goal_y: status=consumed; consumers=target.offset.y (add)
    - approach_goal_z: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_x: status=consumed; consumers=target.offset.x (add)
    - place_y: status=consumed; consumers=target.offset.y (add)
    - place_z: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.166
- **task_score** (E): 1.000
- **fitness_score**: 0.986  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.820

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1738 |
| descend_to_grasp | 1.00 | 1.00 | 0.1119 |
| grasp | 1.00 | 1.00 | 0.0120 |
| lift | 0.67 | 1.00 | 0.1626 |
| approach_goal | 0.00 | 1.00 | 0.1466 |
| descend_to_place | 1.00 | 1.00 | 0.1034 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.523, -0.022, 0.133) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.523, -0.022, 0.133)→(0.505, -0.009, 0.025) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.505, -0.009, 0.025)→(0.496, -0.009, 0.017) | (0.493, -0.015, 0.026)→(0.492, -0.009, 0.024) | 0.281→0.277 | 1.00 / 44.667 | 0.212 | 0.354 |
| lift | lift | 0.67 / step_budget | (0.496, -0.009, 0.017)→(0.489, -0.009, 0.179) | (0.492, -0.009, 0.024)→(0.499, -0.009, 0.181) | 0.277→0.233 | 1.00 / 39.000 | 0.077 | 1.038 |
| approach_goal | approach | 0.00 / step_budget | (0.489, -0.009, 0.179)→(0.586, 0.092, 0.214) | (0.499, -0.009, 0.181)→(0.590, 0.092, 0.203) | 0.233→0.104 | 1.00 / 39.667 | 0.077 | 0.110 |
| descend_to_place | descend | 1.00 / step_budget | (0.586, 0.092, 0.214)→(0.631, 0.171, 0.169) | (0.590, 0.092, 0.203)→(0.633, 0.171, 0.154) | 0.104→0.015 | 1.00 / 39.000 | 0.078 | 0.127 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.040
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.719
- phase_breakdown.lift_object_score: 0.903
- phase_breakdown.reach_object_score: 0.139
- phase_breakdown.place_goal_score: 0.839
- grasp_place_fitness: 0.994

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.994
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.164
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.335


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02158,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":0.01723,"approach_goal.approach_goal_y":-0.03159,"approach_goal.approach_goal_z":0.04493,"approach_goal.approach_speed":0.17926,"approach_object.approach_offset_x":0.04971,"approach_object.approach_offset_y":0.01196,"approach_object.approach_offset_z":0.08273,"descend_to_grasp.descend_grasp_x":0.01813,"descend_to_grasp.descend_grasp_y":0.00494,"descend_to_grasp.descend_grasp_z":-0.00682,"descend_to_place.place_x":0.00119,"descend_to_place.place_y":0.01419,"descend_to_place.place_z":0.01441,"lift.lift_height":0.19343},"optimized_scores":{"best_composite_score":0.15984,"best_fitness_score":0.97984,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.47251,-0.01342,-0.00152],"force_p95":0.80616,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.10621,"mean_force":0.13029,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48182,-0.01437,0.01773]},{"body_a":"grasp_target","body_b":"hand","contact_count":646.0,"contact_point_centroid":[0.49113,-0.03344,0.10485],"force_p95":0.07487,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42495,"mean_force":0.0284,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47732,-0.01428,0.06661]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47573,-0.01794,-0.00245],"force_p95":0.27055,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33605,"mean_force":0.16879,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48496,-0.01442,0.01639]},{"body_a":"grasp_target","body_b":"hand","contact_count":366.0,"contact_point_centroid":[0.49534,-0.03147,0.05462],"force_p95":0.28323,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30853,"mean_force":0.10226,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48406,-0.01441,0.01548]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.47642,-0.0334,0.09754],"force_p95":0.07242,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30725,"mean_force":0.04928,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47619,-0.01426,0.09565]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.4764,0.00489,0.09754],"force_p95":0.07272,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28464,"mean_force":0.04868,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47619,-0.01426,0.09565]},{"body_a":"world","body_b":"grasp_target","contact_count":2264.0,"contact_point_centroid":[0.47616,-0.02015,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50881,-0.00373,0.20993]},{"body_a":"world","body_b":"grasp_target","contact_count":1676.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50473,-0.01092,0.07114]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3988.0,"contact_point_centroid":[0.48397,0.00467,0.01714],"force_p95":0.07733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10423,"mean_force":0.04529,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48377,-0.01442,0.01519]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.53136,0.01598,0.19381],"force_p95":0.07076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10181,"mean_force":0.04826,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53111,0.03512,0.19192]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5484.0,"contact_point_centroid":[0.48402,-0.03467,0.01714],"force_p95":0.07926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10008,"mean_force":0.04937,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48381,-0.01442,0.01523]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.60743,0.14657,0.20035],"force_p95":0.0708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08573,"mean_force":0.04815,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6072,0.12743,0.19853]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.60754,0.1083,0.20048],"force_p95":0.07062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08568,"mean_force":0.04794,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6072,0.12743,0.19853]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.53136,0.05425,0.1938],"force_p95":0.0721,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08384,"mean_force":0.04829,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53111,0.03512,0.19192]}],"total_contact_groups":14},"final_pose_error":0.01403,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62519,0.165,0.1859],"final_tcp_position":[0.62539,0.16503,0.19576],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.10621,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":567.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2264.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.51998,-0.00759,0.12067],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":419.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1676.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.4919,-0.01446,0.02344],"tcp_start":[0.51998,-0.00759,0.12067],"tcp_to_object_dist_end":0.01693,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47536,-0.01423,0.02458],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.286,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1927,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11638.0,"raw_peak_contact_force":0.33605,"tcp_end":[0.48376,-0.01439,0.01517],"tcp_start":[0.4919,-0.01446,0.02344],"tcp_to_object_dist_end":0.01261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47783,-0.01417,0.18182],"object_pos_start":[0.47536,-0.01423,0.02458],"object_to_goal_dist_end":0.23176,"object_to_goal_dist_start":0.286,"object_z_max":0.18162,"peak_contact_force":0.07172,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40818.0,"raw_peak_contact_force":1.10621,"subtask_id":"lift_object","tcp_end":[0.47308,-0.01418,0.17787],"tcp_start":[0.48376,-0.01439,0.01517],"tcp_to_object_dist_end":0.00618,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58726,0.08051,0.20257],"object_pos_start":[0.47783,-0.01417,0.18182],"object_to_goal_dist_end":0.0911,"object_to_goal_dist_start":0.23176,"object_z_max":0.20256,"peak_contact_force":0.07295,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40000.0,"raw_peak_contact_force":0.10181,"subtask_id":"place_goal","tcp_end":[0.58739,0.08048,0.20863],"tcp_start":[0.47308,-0.01418,0.17787],"tcp_to_object_dist_end":0.00606,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62519,0.165,0.1859],"object_pos_start":[0.58726,0.08051,0.20257],"object_to_goal_dist_end":0.00946,"object_to_goal_dist_start":0.0911,"object_z_max":0.20257,"peak_contact_force":0.07018,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":40000.0,"raw_peak_contact_force":0.08573,"subtask_id":"place_goal","tcp_end":[0.62539,0.16503,0.19576],"tcp_start":[0.58739,0.08048,0.20863],"tcp_to_object_dist_end":0.00987,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02703,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":-0.01039,"approach_goal.approach_goal_y":-0.0227,"approach_goal.approach_goal_z":0.09511,"approach_goal.approach_speed":0.1893,"approach_object.approach_offset_x":0.04182,"approach_object.approach_offset_y":-0.02607,"approach_object.approach_offset_z":0.09951,"descend_to_grasp.descend_grasp_x":0.01146,"descend_to_grasp.descend_grasp_y":0.01709,"descend_to_grasp.descend_grasp_z":-0.00833,"descend_to_place.place_x":0.00515,"descend_to_place.place_y":-0.00078,"descend_to_place.place_z":0.00758,"lift.lift_height":0.16943},"optimized_scores":{"best_composite_score":0.16428,"best_fitness_score":0.98428,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":198.0,"contact_point_centroid":[0.45562,-0.00979,-0.00191],"force_p95":0.81288,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.10296,"mean_force":0.12306,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45749,-0.01158,0.0168]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45798,-0.02026,-0.00295],"force_p95":0.40673,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44404,"mean_force":0.23591,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46053,-0.01164,0.01455]},{"body_a":"grasp_target","body_b":"hand","contact_count":355.0,"contact_point_centroid":[0.4731,-0.03005,0.07999],"force_p95":0.10194,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44073,"mean_force":0.05869,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45527,-0.01148,0.04158]},{"body_a":"grasp_target","body_b":"hand","contact_count":403.0,"contact_point_centroid":[0.47659,-0.03419,0.05339],"force_p95":0.36992,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38001,"mean_force":0.18921,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45997,-0.01165,0.01401]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20081.0,"contact_point_centroid":[0.45491,-0.03043,0.09694],"force_p95":0.07754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3003,"mean_force":0.05019,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45471,-0.0113,0.09505]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19662.0,"contact_point_centroid":[0.45495,0.00786,0.09549],"force_p95":0.07704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27142,"mean_force":0.05003,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45472,-0.0113,0.09352]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19564.0,"contact_point_centroid":[0.59573,0.14458,0.14761],"force_p95":0.07307,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14421,"mean_force":0.04987,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59547,0.16374,0.14592]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20303.0,"contact_point_centroid":[0.59504,0.18171,0.14839],"force_p95":0.06979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14216,"mean_force":0.04863,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59454,0.16261,0.14686]},{"body_a":"world","body_b":"grasp_target","contact_count":2092.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49731,-0.02354,0.21842]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6572.0,"contact_point_centroid":[0.45969,-0.03575,0.01552],"force_p95":0.09798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13292,"mean_force":0.0581,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45952,-0.01166,0.01359]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19110.0,"contact_point_centroid":[0.5058,0.03481,0.18435],"force_p95":0.07622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12434,"mean_force":0.0525,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50593,0.054,0.18255]},{"body_a":"world","body_b":"grasp_target","contact_count":2308.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48035,-0.02988,0.0774]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2988.0,"contact_point_centroid":[0.45943,0.00742,0.01564],"force_p95":0.0923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1098,"mean_force":0.0463,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45939,-0.01165,0.01346]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21118.0,"contact_point_centroid":[0.50823,0.07585,0.18487],"force_p95":0.07176,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09684,"mean_force":0.04751,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50824,0.05677,0.18291]}],"total_contact_groups":14},"final_pose_error":0.01627,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62564,0.19686,0.10387],"final_tcp_position":[0.62311,0.19688,0.1194],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.10296,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":524.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2092.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49658,-0.04798,0.13753],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":577.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2308.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46716,-0.0117,0.02088],"tcp_start":[0.49658,-0.04798,0.13753],"tcp_to_object_dist_end":0.01772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45778,-0.01106,0.02305],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.29339,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.25973,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11763.0,"raw_peak_contact_force":0.44404,"tcp_end":[0.45938,-0.0116,0.01345],"tcp_start":[0.46716,-0.0117,0.02088],"tcp_to_object_dist_end":0.00974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46763,-0.0109,0.1802],"object_pos_start":[0.45778,-0.01106,0.02305],"object_to_goal_dist_end":0.28069,"object_to_goal_dist_start":0.29339,"object_z_max":0.18002,"peak_contact_force":0.08389,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40296.0,"raw_peak_contact_force":1.10296,"subtask_id":"lift_object","tcp_end":[0.45421,-0.01104,0.17736],"tcp_start":[0.45938,-0.0116,0.01345],"tcp_to_object_dist_end":0.01372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56317,0.11534,0.17998],"object_pos_start":[0.46763,-0.0109,0.1802],"object_to_goal_dist_end":0.13209,"object_to_goal_dist_start":0.28069,"object_z_max":0.18032,"peak_contact_force":0.07874,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40228.0,"raw_peak_contact_force":0.12434,"subtask_id":"place_goal","tcp_end":[0.55774,0.11536,0.19108],"tcp_start":[0.45421,-0.01104,0.17736],"tcp_to_object_dist_end":0.01235,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62564,0.19686,0.10387],"object_pos_start":[0.56317,0.11534,0.17998],"object_to_goal_dist_end":0.01594,"object_to_goal_dist_start":0.13209,"object_z_max":0.17998,"peak_contact_force":0.06926,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":39867.0,"raw_peak_contact_force":0.14421,"subtask_id":"place_goal","tcp_end":[0.62311,0.19688,0.1194],"tcp_start":[0.55774,0.11536,0.19108],"tcp_to_object_dist_end":0.01573,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01471,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":0.00793,"approach_goal.approach_goal_y":-0.03021,"approach_goal.approach_goal_z":0.0945,"approach_goal.approach_speed":0.15195,"approach_object.approach_offset_x":0.01704,"approach_object.approach_offset_y":-0.01315,"approach_object.approach_offset_z":0.10482,"descend_to_grasp.descend_grasp_x":0.01679,"descend_to_grasp.descend_grasp_y":-0.00072,"descend_to_grasp.descend_grasp_z":-0.00546,"descend_to_place.place_x":0.00164,"descend_to_place.place_y":-0.00492,"descend_to_place.place_z":0.00962,"lift.lift_height":0.21346},"optimized_scores":{"best_composite_score":0.17381,"best_fitness_score":0.99381,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":182.0,"contact_point_centroid":[0.54061,-0.00272,-0.00149],"force_p95":0.65927,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.90544,"mean_force":0.10914,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54386,-0.00154,0.02391]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.54105,0.01756,0.10226],"force_p95":0.07405,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35796,"mean_force":0.04963,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54083,-0.00158,0.10036]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.54108,-0.02073,0.10224],"force_p95":0.07381,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31909,"mean_force":0.04888,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54083,-0.00158,0.10036]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54423,0.0006,-0.00231],"force_p95":0.19921,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28092,"mean_force":0.14611,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54722,-0.00149,0.02315]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4678.0,"contact_point_centroid":[0.54614,-0.02069,0.02353],"force_p95":0.07855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15363,"mean_force":0.04523,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54592,-0.0015,0.02161]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11085.0,"contact_point_centroid":[0.62983,0.10242,0.21087],"force_p95":0.08403,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15098,"mean_force":0.05681,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62993,0.12163,0.2098]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13466.0,"contact_point_centroid":[0.63004,0.14028,0.21082],"force_p95":0.06917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14206,"mean_force":0.04683,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62977,0.12131,0.21003]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.52526,-0.00552,0.21895]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.55241,-0.00547,0.07485]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19066.0,"contact_point_centroid":[0.57661,0.0232,0.21258],"force_p95":0.07752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10524,"mean_force":0.05215,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57664,0.04235,0.21068]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20451.0,"contact_point_centroid":[0.57724,0.06199,0.21269],"force_p95":0.07291,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09982,"mean_force":0.04933,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57711,0.04291,0.21107]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5136.0,"contact_point_centroid":[0.54613,0.01792,0.02355],"force_p95":0.07943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08865,"mean_force":0.045,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54593,-0.0015,0.02163]}],"total_contact_groups":12},"final_pose_error":0.01007,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64816,0.14993,0.17373],"final_tcp_position":[0.64437,0.15007,0.19248],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.90544,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":574.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.55301,-0.01115,0.14013],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.5546,-0.00139,0.03195],"tcp_start":[0.55301,-0.01115,0.14013],"tcp_to_object_dist_end":0.01215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54411,-0.00153,0.02489],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25263,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.18244,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11614.0,"raw_peak_contact_force":0.28092,"tcp_end":[0.54589,-0.00151,0.02158],"tcp_start":[0.5546,-0.00139,0.03195],"tcp_to_object_dist_end":0.00376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55062,-0.00157,0.1811],"object_pos_start":[0.54411,-0.00153,0.02489],"object_to_goal_dist_end":0.18708,"object_to_goal_dist_start":0.25263,"object_z_max":0.18091,"peak_contact_force":0.07512,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40182.0,"raw_peak_contact_force":0.90544,"subtask_id":"lift_object","tcp_end":[0.54062,-0.00158,0.18219],"tcp_start":[0.54589,-0.00151,0.02158],"tcp_to_object_dist_end":0.01007,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61869,0.08156,0.22583],"object_pos_start":[0.55062,-0.00157,0.1811],"object_to_goal_dist_end":0.08887,"object_to_goal_dist_start":0.18708,"object_z_max":0.2258,"peak_contact_force":0.07962,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39517.0,"raw_peak_contact_force":0.10524,"subtask_id":"place_goal","tcp_end":[0.61178,0.08164,0.24087],"tcp_start":[0.54062,-0.00158,0.18219],"tcp_to_object_dist_end":0.01655,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":636.0,"n_steps_budget":1000.0,"object_pos_end":[0.64816,0.14993,0.17373],"object_pos_start":[0.61869,0.08156,0.22583],"object_to_goal_dist_end":0.0192,"object_to_goal_dist_start":0.08887,"object_z_max":0.22583,"peak_contact_force":0.09388,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":24551.0,"raw_peak_contact_force":0.15098,"subtask_id":"place_goal","tcp_end":[0.64437,0.15007,0.19248],"tcp_start":[0.61178,0.08164,0.24087],"tcp_to_object_dist_end":0.01913,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```